from __future__ import print_function

# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #2: Run simple mission using raw XML

from builtins import range
import MalmoPython
import os
import sys
import time
from random import randint


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
    **kwargs,
):
    """
    Generate Malmo mission XML string of an hide and seek arena with the requested settings.

    Args:
        arena_size (int):
            Specify the size of the square play area for the agents. Resulting play area will be of size (arena_size * arena_size). Does not include the walls of the arena.
        is_closed_arena (bool):
            Specify if the area will be closed by walls. A closed arena will result in rooms. An open arena will still generate dividers that would've created the rooms, but the outer wall isn't generated which
            will act as obstacles instead.
        **kwargs:
            Arbitrary keyword arguments.

        Keyword Arguments:
            num_rooms (int):
                Specify the number of rooms to divide the arena into. The doors in between rooms will be randomly placed. If is_open_arena=True, the walls creating the rooms will still generate but will act as obstacles instead.
            gen_blocks (bool):
                Specify if the mission should randomly generate blocks for the agents to pick up and place.
            num_blocks (int):
                Specify the number of blocks that should be generated.

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

    # add map generation
    mission_string += f"""
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,2;1;"/>
                <DrawingDecorator>"""
    # reset blocks at arena
    mission_string += f"""
                    <DrawCuboid x1='-1000' x2='1000' y1='1' y2='1' z1='-1000' z2='1000' type='grass'/>
                    <DrawCuboid x1='-1000' x2='1000' y1='2' y2='4' z1='-1000' z2='1000' type='air'/>"""
    # generate floor
    mission_string += f"""
                    <DrawCuboid x1='0' x2='{arena_size - 1}' y1='1' y2='1' z1='0' z2='{arena_size - 1}' type='iron_block'/>"""
    # generate walls
    if is_closed_arena:
        mission_string += f"""
                    <DrawCuboid x1='-1' x2='{arena_size}' y1='2' y2='3' z1='-1' z2='{arena_size}' type='stonebrick'/>
                    <DrawCuboid x1='0' x2='{arena_size - 1}' y1='2' y2='3' z1='0' z2='{arena_size - 1}' type='air'/>"""

    # generate room dividers/obstacles
    if "num_rooms" in kwargs:
        num_rooms = kwargs["num_rooms"]
        if type(num_rooms) == tuple:
            num_rooms = randint(num_rooms)
    else:
        num_rooms = randint(1, 3)

    # 2D area of PLAY AREA
    play_arena = [[0 for _ in range(arena_size)] for _ in range(arena_size)]

    last_was_horizontal = True
    vertical_door_indices = set()
    horizontal_door_indices = set()

    print(num_rooms)

    if num_rooms != 1:
        for _ in range(num_rooms - 1):
            # don't want to place dividers against the outter walls
            wall_index = randint(3, arena_size - 4)

            print(f"wall_index: {wall_index}")

            # vertical divider
            if last_was_horizontal:
                print(f"Creating a vertical divider at index {wall_index}")

                # start divider from top
                if randint(-1, 1) > 0:
                    print("     starting divider from top")
                    for i in range(arena_size):
                        if play_arena[i][wall_index] == 1:
                            break
                        play_arena[i][wall_index] = 1

                    # create door within divider
                    door_index = randint(0, i - 1)
                    print(f"door_index: {door_index}")
                    play_arena[door_index][wall_index] = 0
                    horizontal_door_indices.add(wall_index)

                # start divider from bottom
                else:
                    print("     starting divider from bottom")
                    for i in range(arena_size - 1, -1, -1):
                        if play_arena[i][wall_index] == 1:
                            break
                        play_arena[i][wall_index] = 1

                    # create door within divider
                    door_index = randint(i, arena_size - 1)
                    print(f"door_index: {door_index}")
                    play_arena[door_index][wall_index] = 0
                    horizontal_door_indices.add(wall_index)

            # horizontal divider
            else:
                print(f"Creating a horizontal divider at index {wall_index}")

                # start divider from left
                if randint(-1, 1) < 0:
                    print("     starting divider from left")
                    for i in range(arena_size):
                        if play_arena[wall_index][i] == 1:
                            break
                        play_arena[wall_index][i] = 1

                    # create door within divider
                    door_index = randint(0, i - 1)
                    print(f"door_index: {door_index}")
                    play_arena[wall_index][door_index] = 0
                    vertical_door_indices.add(door_index)

                # start divider from right
                else:
                    print("     starting divider from right")
                    for i in range(arena_size - 1, -1, -1):
                        if play_arena[wall_index][i] == 1:
                            break
                        play_arena[wall_index][i] = 1

                    # create door within divider
                    door_index = randint(i + 1, arena_size - 1)
                    print(f"door_index: {door_index}")
                    play_arena[wall_index][door_index] = 0
                    horizontal_door_indices.add(wall_index)

            last_was_horizontal = not last_was_horizontal

    for i in play_arena:
        print(i)
    # exit()
    for row_index in range(len(play_arena)):
        for col_index in range(len(play_arena)):
            if play_arena[row_index][col_index] == 1:
                mission_string += f"""
                    <DrawBlock x='{col_index}'  y='{2}' z='{row_index}' type='cobblestone'/>"""

    # mission_string += f"""
    #                 <DrawCuboid x1='-{arena_size//2 + 1}' x2='{arena_size//2 + 1}' y1='2' y2='3' z1='-{arena_size//2 + 1}' z2='{arena_size//2 + 1}' type='stonebrick'/>
    # """

    # add quit condition
    mission_string += f"""
                </DrawingDecorator>
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
        num_rooms=3,
    )
    print(mission_xml)
    # print(mission_xml)
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
