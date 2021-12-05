import numpy as np
import random
import time
import uuid
import json

import gym

try:
    from malmo import MalmoPython
except:
    import MalmoPython
from gym.spaces import Box, Dict
from gym.vector.utils import batch_space
from stable_baselines3 import A2C, SAC
from stable_baselines3.common.vec_env import DummyVecEnv

from env import create_env
from multi_agent_helper import safeStartMission, safeWaitForStart

class SingleAgentEnv(gym.Env):

    def __init__(self, agent_id, obs_size, init_malmo_callback, seeker_found_hider_callback, hider = True, max_steps=40):
        ### Env Parameters ###
        self.obs_size = obs_size
        self.agent_id = agent_id
        self.hider = hider
        self.action_space = Box(-1,1, shape = (4,), dtype=np.float32)
        self.observation_space = Dict( {
            "cursor" : Box(0, 1, shape = (3,), dtype = np.float32),
            "facing" : Box(-360, 360, shape = (2,), dtype=np.float32),
            "grid" : Box(0, 2, shape = (2 * self.obs_size * self.obs_size,), dtype=np.float32)
        })

        ### Malmo Parameters ###
        self.agent_host = MalmoPython.AgentHost()
        self.init_malmo = init_malmo_callback
        self.seeker_found_hider = seeker_found_hider_callback

        ### Agent State ###
        self.max_steps = max_steps
        self.episode_step = 0
        self.reward_given = False
        self.staring_at_sky = False
        self.explored_cells = set()
        self.reward_explore = False
    
    def reset(self):
        self.explored_cells = set()      
        if self.episode_step > 0 and self.hider:
            print("attempting to end mission")
            self.agent_host.sendCommand(f"quit")
        if not self.agent_host.getWorldState().is_mission_running:
            self.init_malmo()
        return self.get_observation()
    
    def step(self, action):
        reward = 0
        info = {}
        obs = {
            "cursor" : np.zeros((3,), dtype=np.float32),
            "facing" : np.zeros((2,), dtype=np.float32),
            "grid" : np.zeros((2 * self.obs_size * self.obs_size), dtype = np.float32)
        }
        self.execute_malmo_action(action)
        world_state = self.agent_host.getWorldState()
        self.episode_step += 1
        if not world_state.is_mission_running:
            print("agent is done!")
            return obs, reward, True, info
        for r in world_state.rewards:
            reward += r.getValue()
        obs = self.get_observation()
        if self.staring_at_sky:
            reward -= 1
            self.staring_at_sky = False
        if not self.hider and self.reward_explore:
            reward += 1
            self.reward_explore = False
            print("reward added for exploring new cell")
        if self.seeker_found_hider() and self.reward_given == False:
            if self.hider:
                print("rewards applied to hider")
                reward -= 50
                self.seeker_found_hider(hidden=True)
            else:
                print("rewards applied to seeker")
                reward += 100
                self.reward_given = True
        return obs, reward, False, info
    
    def get_observation(self):
        obs = {
            "cursor" : np.zeros((3,), dtype=np.float32),
            "facing" : np.zeros((2,), dtype=np.float32),
            "grid" : np.zeros((2 * self.obs_size * self.obs_size), dtype = np.float32)
        }
        while self.agent_host.getWorldState().is_mission_running:
            world_state = self.agent_host.getWorldState()
            if world_state.number_of_observations_since_last_state > 0:
                malmo_obs = json.loads(world_state.observations[-1].text)
                if "LineOfSight" in malmo_obs:
                    los = malmo_obs["LineOfSight"]
                    if "hider" in los["type"] and not self.hider:
                        print("seeker found hider! rewards to be applied")
                        self.seeker_found_hider(spotted=True)
                        obs["cursor"][2] = 1
                    elif los["type"] in ("cobblestone", "stonebrick"):
                        obs["cursor"][0] = 1
                    elif los["type"] in ("dirt"):
                        obs["cursor"][1] = 1
                else:
                    self.staring_at_sky = True
                obs["facing"][0] = malmo_obs["Yaw"]
                obs["facing"][1] = malmo_obs["Pitch"]
                grid = malmo_obs['floorAll']
                for i, x in enumerate(grid):
                    if x == 'cobblestone' or x == 'stone_brick':
                        obs["grid"][i] = 1
                    elif x == 'dirt':
                        obs["grid"][i] = 2
                
                if not self.hider:
                    loc = (int(malmo_obs["XPos"]), int(malmo_obs["YPos"]))
                    if loc not in self.explored_cells:
                        self.reward_explore = True
                        self.explored_cells.add(loc)
                break
        return obs
    
    def execute_malmo_action(self, action):
        self.agent_host.sendCommand(f"move {action[0]}")
        self.agent_host.sendCommand(f"turn {action[1]}")
        self.agent_host.sendCommand(f"pitch {action[2]}")
        if action[3] > 0:
            if self.hider:
                self.execute_malmo_action([0,0,0,0])
                self.agent_host.sendCommand(f"use 1")
            if not self.hider:
                self.execute_malmo_action([0,0,0,0])
                self.agent_host.sendCommand(f"attack 1")
                time.sleep(0.2)
        time.sleep(0.2)
    
    def __repr__(self):
        return self.agent_id


class HideAndSeekMission:

    metadata = {'render.modes': ['human'], "name": "HideAndSeek"}

    def __init__(self):
        ### Arena Parameters ###
        self.arena_size = 10
        self.closed_arena = True
        self.env_type = "quadrant"
        self.gen_num_blocks = 0
        self.gen_num_stairs = 0

        ### Agent Parameters ###
        self.obs_size = 7
        self.num_hiders = 1
        assert self.num_hiders > 0, "hiders are mandatory"
        self.num_seekers = 1
        self.max_episode_steps = 300

        ### Multi-Model State ###
        self.num_runs = 10
        self.seeker_phase_duration = 40
        self.hider_phase_duration = 40
        self.target_model = SAC
        self.possible_hiders = [f"hider_{x}" for x in range(self.num_hiders)]
        self.possible_seekers = [f"seeker_{x}" for x in range(self.num_seekers)]
        self.hider_agents = {key:SingleAgentEnv(key, self.obs_size, self.init_malmo, self.seeker_found_hider_check, hider = True) for key in self.possible_hiders}
        self.seeker_agents = {key:SingleAgentEnv(key, self.obs_size, self.init_malmo, self.seeker_found_hider_check, hider = False) for key in self.possible_seekers}
        try:
            print("attempting to load hider...")
            self.hider_model = self.target_model.load("sac_hider", self.hider_agents["hider_0"])
        except:
            print("could not find hider")
            self.hider_model = self.target_model("MultiInputPolicy", self.hider_agents["hider_0"], learning_starts=10)
        try:
            print("attempting to load seeker...")
            self.seeker_model = self.target_model.load("sac_seeker", self.seeker_agents["seeker_0"])
        except:
            print("could not find seeker")
            self.seeker_model = self.target_model("MultiInputPolicy", self.seeker_agents["seeker_0"], learning_starts=10)
        self.seeker_found_hider = False

        ### Malmo State ###
        self.malmo_agents = { **{key : self.hider_agents[key].agent_host for key in self.possible_hiders}, **{key : self.seeker_agents[key].agent_host for key in self.possible_seekers}}
        self.malmo_agents["Observer"] = MalmoPython.AgentHost()

    def init_malmo(self):
        self.hider_agents["hider_0"].episode_step = 0
        self.seeker_agents["seeker_0"].episode_step = 0
        self.seeker_agents["seeker_0"].reward_given = False
        self.seeker_found_hider = False
        my_mission = MalmoPython.MissionSpec(
            self.gen_mission_xml(
                self.arena_size,
                self.closed_arena,
                self.env_type,
                {
                    "blocks_inside": False,
                    "blocks_outside": True,
                    "stairs_inside": False,
                    "stairs_outside": True,
                }, 
                0, 
                0, 
                2
            ), 
            True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.setViewpoint(1)

        my_mission_record.setDestination("mission_viewpoint.tgz")
        my_mission_record.recordMP4(MalmoPython.FrameType.VIDEO, 24, 2000000, False)

        client_pool = MalmoPython.ClientPool()
        for port in range(10000, 10000 + self.num_seekers + self.num_hiders + 1):
            client_pool.add(MalmoPython.ClientInfo('127.0.0.1', port))

        experimentID = str(uuid.uuid4())
        agent_hosts = self.malmo_agents

        for agent_id, agent in enumerate(agent_hosts.keys()):
            agent_hosts[agent].sendCommand("quit")

        for agent_id, agent in enumerate(agent_hosts.keys()):
            time.sleep(1)
            safeStartMission(agent_hosts[agent], my_mission, client_pool, MalmoPython.MissionRecordSpec(), agent_id, experimentID)
            time.sleep(1)

        safeWaitForStart(agent_hosts.values())
        time.sleep(1)
    
    def learn(self):
        self.init_malmo()
        ct = 0
        while ct < self.num_runs:
            ct += 1
            self.hider_model = self.hider_model.learn(self.hider_phase_duration)
            self.hider_agents["hider_0"].execute_malmo_action([0,0,0,0])
            
            self.seeker_model = self.seeker_model.learn(self.seeker_phase_duration)
            self.seeker_agents["seeker_0"].execute_malmo_action([0,0,0,0])
        print("learn finished")
        self.hider_model.save("sac_hider")
        self.seeker_model.save("sac_seeker")
    
    def seeker_found_hider_check(self, spotted=False, hidden=False):
        if hidden:
            self.seeker_found_hider = False
        if spotted:
            self.seeker_found_hider = True
        return self.seeker_found_hider

    def gen_mission_xml(self,
        arena_size: int,
        is_closed_arena: bool,
        env_type: str,
        item_gen,
        num_blocks: int,
        num_stairs: int,
        min_agent_spawn_dist: int,
        **kwargs,
    ):
        """
        Generate Malmo mission XML string of an hide and seek arena with the requested settings.

        Arguments:
            arena_size (int):
                Specify the size of the square play area for the agents. Resulting play area will be of size (arena_size * arena_size). Does not include the walls of the arena.
            is_closed_arena (bool):
                Specify if the area will be closed by walls. A closed arena will result in rooms. An open arena will still generate dividers that would've created the rooms, but the outer walls aren't generated.
            env_type (str):
                Specify what environment type to generate.
                    "quadrant"
                        Results in a single room that is randomly placed in the corner of the play arena.
            item_gen (dict[str,bool]):
                Rules that dictate how blocks and stairs will be generated.
                {
                    "blocks_inside" : bool - Toggles block generation inside quadrant room.
                    "blocks_outside": bool - Toggles block generation inside quadrant room.
                    "stairs_inside" : bool - Toggles stairs generation inside quadrant room.
                    "stairs_outside": bool - Toggles stairs generation inside quadrant room.
                }
            num_blocks (int):
                Specify the number of blocks that should be generated.
            num_stairs (int):
                Specify the number of stairs that should be generated.
            min_agent_spawn_dist (int):
                Specify the minimum distance agents have to spawn from one another
            **kwargs:
                Arbitrary keyword arguments. Each environment type has additional settings that can be tweaked. Refer to those individual functions to find out more.

        Returns:
            str: A formated Malmo mission XML string with the requested settings.
        """

        # generate environment and map for environment (doesn't include outer walls)
        # empty = 0
        # walls = 1
        # blocks = 2
        # stairs = 3shoul
        # agents = 4
        env, env_map = create_env(
            arena_size,
            is_closed_arena,
            env_type,
            item_gen,
            num_blocks,
            num_stairs,
            **kwargs,
        )

        # generate positions for agents
        agent_pos = []
        attempt_counter = 0
        max_attempts = 5
        while len(agent_pos) != self.num_hiders + self.num_seekers:
            while True:
                # reset all generated agent positions to prevent situations where in initial generated 
                # agent positions prevents generation of the remaining agents
                attempt_counter += 1
                if attempt_counter == max_attempts:
                    for pos in agent_pos:
                        env_map[pos[1]][pos[0]] = 0
                    agent_pos = []

                    continue

                x_pos = random.randint(0, arena_size - 1)
                y_pos = random.randint(0, arena_size - 1)

                # prevent agents from spawning in walls
                if env_map[y_pos][x_pos] == 1:
                    continue
                
                # prevent agents from spawning too close to one another
                adjacent_spots = []

                # generate all spaces around potential spawn point, up to min_agent_spawn_dist inclusive
                for row_index in range(-(min_agent_spawn_dist), min_agent_spawn_dist + 1):
                    for col_index in range(-(min_agent_spawn_dist), min_agent_spawn_dist + 1):
                        # only consider VALID spots
                        if 0 <= (y_pos + col_index) < len(env_map) and 0 <= (x_pos + row_index) < len(env_map[0]):
                            adjacent_spots.append((y_pos + col_index, x_pos + row_index))

                # an agent was found within min_agent_spawn_dist
                if any([True for i in adjacent_spots if env_map[i[0]][i[1]] == 4]):
                    continue
                
                # valid position for agent
                agent_pos.append((x_pos, y_pos))
                env_map[y_pos][x_pos] = 4
                attempt_counter = 0
                break

        mission_string = f""

        # add boiler plate stuff
        mission_string += """
        <?xml version="1.0" encoding="UTF-8" standalone="no" ?>
        <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <About>
                <Summary>Multi Agent Hide and Seek</Summary>
            </About>"""

        # add server settings
        mission_string += f"""
            <ServerSection>
                <ServerInitialConditions>
                    <Time>
                        <StartTime>12000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                    </Time>
                    <Weather>clear</Weather>
                </ServerInitialConditions>"""

        mission_string += f"""{env}"""

        # add quit condition
        # todo change quit conditions to have a proper time limit
        mission_string += f"""
                    <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
            </ServerSection>"""

        # set up hiders
        for i in range(self.num_hiders):
            # randomize agent starting position
            mission_string += f"""<AgentSection mode="Survival">
                <Name>{self.possible_hiders[i]}</Name>
                <AgentStart>
                    <Placement x="{str(agent_pos[i][1])}" y="2" z="{str(agent_pos[i][0])}"/>
                    <Inventory>
                        <InventoryItem slot="0" type="dirt" quantity="8"/>
                    </Inventory>
                </AgentStart>
                <AgentHandlers>
                    <ContinuousMovementCommands turnSpeedDegs="360"/>
                    <MissionQuitCommands/>
                    <ObservationFromFullStats/>                    
                    <ObservationFromRay/>
                    <ObservationFromGrid>
                        <Grid name="floorAll">
                        <min x="-{str(int(self.obs_size/2))}" y="-1" z="-{str(int(self.obs_size/2))}"/>
                        <max x="{str(int(self.obs_size/2))}" y="0" z="{str(int(self.obs_size/2))}"/>
                        </Grid>
                    </ObservationFromGrid>
                </AgentHandlers>
            </AgentSection>"""
        
        #set up seekers
        for i in range(self.num_seekers):
            # randomize agent starting position
            mission_string += f"""<AgentSection mode="Survival">
                <Name>{self.possible_seekers[i]}</Name>
                <AgentStart>
                    <Placement x="{str(agent_pos[self.num_hiders + i][1])}" y="2" z="{str(agent_pos[self.num_hiders + i][0])}" pitch="90"/>
                    <Inventory>
                        <InventoryItem slot="0" type="iron_shovel"/>
                    </Inventory>
                </AgentStart>
                <AgentHandlers>
                    <ContinuousMovementCommands turnSpeedDegs="360"/>
                    <MissionQuitCommands/>
                    <ObservationFromFullStats/>
                    <ObservationFromRay/>
                    <ObservationFromGrid>
                        <Grid name="floorAll">
                        <min x="-{str(int(self.obs_size/2))}" y="-1" z="-{str(int(self.obs_size/2))}"/>
                        <max x="{str(int(self.obs_size/2))}" y="0" z="{str(int(self.obs_size/2))}"/>
                        </Grid>
                    </ObservationFromGrid>
                </AgentHandlers>
            </AgentSection>"""

        # setup agent as observer
        mission_string += f"""
            <AgentSection mode="Spectator">
                <Name>TopDownView</Name>
                <AgentStart>
                    <Placement x="{arena_size/2}" y="{10 + (arena_size//3)}" z="{arena_size/2}" pitch="90" yaw="180"/>
                </AgentStart>
                <AgentHandlers>
                    <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
            </AgentSection>
        </Mission>"""

        return mission_string

if __name__ == '__main__':
    env = HideAndSeekMission()
    num_cycles = 500
    for _ in range(num_cycles):
        env.learn()
    # parallel_api_test(env, num_cycles=5)