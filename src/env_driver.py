from __future__ import print_function

from builtins import range
import MalmoPython
import os
import sys
import time
from random import randint
from typing import Dict

from env import create_env

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(
        sys.stdout.fileno(), "w", 0
    )  # flush print output immediately
else:
    import functools

    print = functools.partial(print, flush=True)


def gen_mission_xml(
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

    mission_string += f"""{create_env(arena_size, is_closed_arena, env_type, num_blocks, num_stairs, **kwargs)}"""

    # add quit condition
    mission_string += f"""
                <ServerQuitFromTimeUp description="" timeLimitMs="1"/>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>"""

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


# Create default Malmo objects:
agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse(sys.argv)
except RuntimeError as e:
    print("ERROR:", e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

while True:
    # setup Malmo mission
    mission_xml = gen_mission_xml(
        arena_size=10,
        is_closed_arena=True,
        env_type="quadrant",
        item_gen={
            "blocks_inside": True,
            "blocks_outside": True,
            "stairs_inside": True,
            "stairs_outside": True,
        },
        num_blocks=5,
        num_stairs=3,
        quadrant_loc=3,
        quadrant_num_doors=2,
    )
    print(mission_xml)
    my_mission = MalmoPython.MissionSpec(mission_xml, True)
    my_mission_record = MalmoPython.MissionRecordSpec()

    # Attempt to start a mission:
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission(my_mission, my_mission_record)
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                time.sleep(2)

    # Loop until mission starts:
    print("Waiting for the mission to start ", end=" ")
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    print()
    print("Mission running ", end=" ")

    # Loop until mission ends:
    while world_state.is_mission_running:
        break

    print()
    print("Mission ended")

    input()
