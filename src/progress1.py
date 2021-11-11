try:
    from malmo import MalmoPython
except:
    import MalmoPython
from env import create_env
from multi_agent_helper import safeStartMission, safeWaitForStart
from typing import Dict
import time
import uuid
import json
import numpy as np
import random

import gym
from gym.spaces import Box, Dict

### TARGET RL ALGORITHM: Soft Actor Critic ###
from stable_baselines3 import SAC


class HideAndSeekMission(gym.Env):
    def __init__(self, env_config):
        ### Arena Parameters ###
        self.arena_size = 0
        self.closed_arena = True
        self.env_type = "quadrant"
        self.gen_num_blocks = 0
        self.gen_num_stairs = 0

        ### Agent Parameters ###
        self.obs_size = 5
        self.num_agents = 2
        self.max_episode_steps = 150
        self.agent_hosts = [MalmoPython.AgentHost()]
        self.agent_hosts += [MalmoPython.AgentHost() for _ in range(1, self.num_agents + 1)]

        ### Misc Parameters ###
        self.log_frequency = 2

        ### Malmo Mission State ###
        self.client_pool = None
        self.mission = None
        self.mission_record = None
        self.agents = []
    
    def reset(self):
        """
        Resets the environment for the next episode.

        Returns
            observation: <np.array> flattened initial obseravtion
        """
        world_state = self.init_malmo()

        self.returns.append(self.episode_return)
        current_step = self.steps[-1] if len(self.steps) > 0 else 0
        self.steps.append(current_step + self.episode_step)
        self.episode_return = 0
        self.episode_step = 0

        if len(self.returns) > self.log_frequency + 1 and \
            len(self.returns) % self.log_frequency == 0:
            print("Logging returns...")
            self.log_returns()

        #Get Observation for each agent
        self.obs = [agent.get_observation(world_state) for agent in self.agent_hosts]

        return self.obs

    def step(self, action):
        """
        Take an action in the environment and return the results.

        Args
            action: vector of actions taken from RL agent

        Returns
            observation: <np.array> flattened array of obseravtion
            reward: <int> reward from taking action
            done: <bool> indicates terminal state
            info: <dict> dictionary of extra information
        """

        obs = None
        reward = None
        done = False

        ## placeholder code
        for i in range(self.num_agents):
            commands = [
                'move ' + str(action[0]),
                'turn ' + str(action[1]),
            ]
            for command in commands:
                self.agent_hosts[i].sendCommand(command)
                time.sleep(.2)

            world_state = self.agent_hosts[i].getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
        
        return self.obs, reward, done, dict()
        

    def gen_mission_xml(self,
        arena_size: int,
        is_closed_arena: bool,
        env_type: str,
        item_gen: Dict[str, bool],
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
        for i in range(self.num_agents):
            # randomize agent starting position
            pos_x = random.randint(0, arena_size)
            pos_z = random.randint(0, arena_size)
            while env_map[pos_z][pos_x] != 0:
                pos_x = random.randint(0, arena_size)
                pos_z = random.randint(0, arena_size)

            mission_string += f"""<AgentSection mode="Survival">
                <Name>"Seeker {str(i)}"</Name>
                <AgentStart>
                    <Placement x="{str(pos_x)}" y="2" z="{str(pos_z)}"/>
                </AgentStart>
                <AgentHandlers>
                    <ContinuousMovementCommands turnSpeedDegs="360"/>
                    <ObservationFromRay/>
                    <ObservationFromFullStats/>
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
                    <ObservationFromFullStats/>
                    <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
            </AgentSection>
        </Mission>"""

        return mission_string

    def init_malmo(self):
        """
        Initialize new malmo mission.
        """
        my_mission = MalmoPython.MissionSpec(self.get_mission_xml(), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(1)

        client_pool = MalmoPython.ClientPool()
        for port in range(10000, 10000 + self.num_agents + 1):
            client_pool.add(MalmoPython.ClientInfo('127.0.0.1', port))

        experimentID = str(uuid.uuid4())

        for i in range(len(self.agent_hosts)):
            safeStartMission(self.agent_hosts[i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), i, experimentID)

        safeWaitForStart(self.agent_hosts)
        time.sleep(1)

        world_states = []
        for agent_host in self.agent_hosts:
            world_state = agent_host.getWorldState()
            while not world_state.has_mission_begun:
                time.sleep(0.1)
                world_state = agent_host.getWorldState()
                for error in world_state.errors:
                    print("\nError:", error.text)
            world_states.append(world_state)

        return world_states

class PlayerAgent:

    def __init__(self, obs_size):
        self.obs_size = obs_size
        self.action_space = Box(np.array([-1,-1,-1]), np.array([1,1,1]))
        self.observation_space = Dict({
            "yaw":Box(-360, 360, shape=(1, ), dtype = np.float32),
            "grid":Box(0, 1, shape=(2 * self.obs_size * self.obs_size, ), dtype=np.float32)}
        )
        self.obs = None
        self.allow_tag = False

        ### Logging information ###
        self.timestamp = time.time()
        self.episode_step = 0
        self.episode_return = 0
        self.returns = []
        self.steps = []

        ### Agent Host initialization ###
        self.agent_host = MalmoPython.AgentHost()
    
    def get_observation(self, world_state):
        obs = {"yaw":np.zeros((1,)), "grid":np.zeros((2 * self.obs_size * self.obs_size, ))}
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                observations = json.loads(msg)

                grid = observations['floorAll']
                for i, x in enumerate(grid):
                    obs["grid"][i] = x == 'cobblestone' or x == "stone_brick"
                obs["yaw"] = np.array([observations['Yaw']])                
                break

        return obs, False