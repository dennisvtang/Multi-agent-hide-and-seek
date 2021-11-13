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

    def __init__(self, agent_id, obs_size):
        ### Env Parameters ###
        self.obs_size = obs_size
        self.agent_id = agent_id
        self.action_space = Box(-1,1, shape = (2,), dtype=np.float32)
        self.observation_space = Box(-360, 360, shape = (2 * self.obs_size * self.obs_size + 1,), dtype=np.float32)

        ### Malmo Parameters ###
        self.agent_host = MalmoPython.AgentHost()
    
    def reset(self):
        return self.get_observation()
    
    def step(self, action):
        reward = 0
        info = {}
        obs = np.zeros((2 * self.obs_size * self.obs_size + 1), dtype = np.float32)
        self.execute_malmo_action(action)
        world_state = self.agent_host.getWorldState()
        if not world_state.is_mission_running:
            return obs, reward, True, info
        for r in world_state.rewards:
            reward += r.getValue()
        obs = self.get_observation()
        return obs, reward, False, info
    
    def get_observation(self):
        obs = np.zeros((2 * self.obs_size * self.obs_size + 1), dtype = np.float32)
        while self.agent_host.getWorldState().is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState(0)
            
            if world_state.number_of_observations_since_last_state > 0:
                malmo_obs = json.loads(world_state.observations[-1].text)
                obs[0] = malmo_obs["Yaw"]
                grid = malmo_obs['floorAll']
                for i, x in enumerate(grid):
                    obs[i+1] = x == 'cobblestone' or x == "stone_brick"
                break
        return obs
    
    def execute_malmo_action(self, action):
        print(self.agent_id)
        self.agent_host.sendCommand(f"move {action[0]}")
        self.agent_host.sendCommand(f"turn {action[1]}")
        time.sleep(0.2)
    
    def __repr__(self):
        return self.agent_id


class HideAndSeekMission(DummyVecEnv):

    metadata = {'render.modes': ['human'], "name": "HideAndSeek"}

    def __init__(self):
        ### Arena Parameters ###
        self.arena_size = 10
        self.closed_arena = True
        self.env_type = "quadrant"
        self.gen_num_blocks = 0
        self.gen_num_stairs = 0

        ### Agent Parameters ###
        self.obs_size = 5
        self.num_hiders = 1
        assert self.num_hiders > 0, "hiders are mandatory"
        self.num_seekers = 1        

        ### Vector Env State ###
        self.is_vector_env = True
        self.num_envs = self.num_hiders + self.num_seekers
        self.possible_agents = [f"hider_{x}" for x in range(self.num_hiders)] + [f"seeker_{x}" for x in range(self.num_seekers)]
        print("Agent ids", self.possible_agents)
        self.agent_envs = {key:SingleAgentEnv(key, self.obs_size) for key in self.possible_agents}
        envs = []
        def create_factory_func(agent_env):
            return lambda: agent_env
        for key in self.possible_agents:
            new_agent_env = self.agent_envs[key]
            print("adding", new_agent_env.agent_id)
            envs.append(create_factory_func(new_agent_env))
        super().__init__(envs)
        # self.action_space = batch_space(self.agent_envs["hider_0"].observation_space, n = len(self.possible_agents))
        # self.observation_space = batch_space(Box(-360, 360, shape = (2 * self.obs_size * self.obs_size + 1,), dtype=np.float32), n = len(self.possible_agents))

        ### Malmo State ###
        self.malmo_agents = {key : self.agent_envs[key].agent_host for key in self.possible_agents}
        self.malmo_agents["Observer"] = MalmoPython.AgentHost()
    
    def reset(self):
        '''
        Resets the environment to a starting state.
        '''
        self.init_malmo()
        # self.agents = self.possible_agents[:]
        # self.init_malmo()
        # observations = np.array([self.agent_envs[agent].reset() for agent in self.agents])
        # return observations
        return super().reset()
    
    def step_wait(self):
        '''
        Receives a dictionary of actions keyed by the agent name.
        Returns the observation dictionary, reward dictionary, done dictionary, and info dictionary,
        where each dictionary is keyed by the agent.
        '''

        # rewards = [0 for _ in range(self.num_envs)]
        # dones = [False for _ in range(self.num_envs)]
        # infos = [{} for _ in range(self.num_envs)]
        # observations = np.array([self.agent_envs[agent].reset() for agent in self.agents])

        # for i, agent in enumerate(self.agents):        
        #     curr_obs, curr_reward, done, info = self.agent_envs[agent].step(actions[i])
        #     rewards[i] = curr_reward
        #     observations[i] = curr_obs
        #     dones[i] = done
        #     infos[i] = info
        # print(rewards)
        # return observations, rewards, dones, infos
        return super().step_wait()

    def init_malmo(self):
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
                }, 0, 0), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(1)

        client_pool = MalmoPython.ClientPool()
        for port in range(10000, 10000 + self.num_seekers + self.num_hiders + 1):
            client_pool.add(MalmoPython.ClientInfo('127.0.0.1', port))

        experimentID = str(uuid.uuid4())
        agent_hosts = self.malmo_agents
        for agent_id, agent in enumerate(agent_hosts.keys()):
            safeStartMission(agent_hosts[agent], my_mission, client_pool, MalmoPython.MissionRecordSpec(), agent_id, experimentID)

        safeWaitForStart(agent_hosts.values())
        time.sleep(1)

    def gen_mission_xml(self,
        arena_size: int,
        is_closed_arena: bool,
        env_type: str,
        item_gen,
        num_blocks: int,
        num_stairs: int,
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
            **kwargs:
                Arbitrary keyword arguments. Each environment type has additional settings that can be tweaked. Refer to those individual functions to find out more.

        Returns:
            str: A formated Malmo mission XML string with the requested settings.
        """

        # generate environment and map for environment (doesn't include outer walls)
        env, env_map = create_env(
            arena_size,
            is_closed_arena,
            env_type,
            item_gen,
            num_blocks,
            num_stairs,
            **kwargs,
        )

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
                    <ServerQuitFromTimeUp description="" timeLimitMs="1"/>
                    <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
            </ServerSection>"""

        # set up agents
        for i in range(self.num_hiders + self.num_seekers):
            # randomize agent starting position
            mission_string += f"""<AgentSection mode="Survival">
                <Name>{self.possible_agents[i]}</Name>
                <AgentStart>
                    <Placement x="{str(random.randint(0, arena_size))}" y="2" z="{str(random.randint(0, arena_size))}"/>
                </AgentStart>
                <AgentHandlers>
                    <RewardForCollectingItem>
                        <Item type="apple" reward="1"/>
                    </RewardForCollectingItem>
                    <ObservationFromFullStats/>
                    <ContinuousMovementCommands turnSpeedDegs="360"/>
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

def wrap_env():
    env = HideAndSeekMission()
    # env = ss.pad_action_space_v0(env)
    # env = ss.pad_observations_v0(env)
    #env = ss.gym_vec_env_v0(env, env.num_envs)
    return env

if __name__ == '__main__':
    env = wrap_env()
    # parallel_api_test(env, num_cycles=5)
    model = A2C("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)
    model.save("multi_sac_hideandseek")
