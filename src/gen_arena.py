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
            Specify if the area will be closed by walls. A closed arena will result in rooms. An open arena will still generate dividers that would've created the rooms, but the outer walls aren't generated.
        **kwargs:
            Arbitrary keyword arguments.

        Keyword Arguments:
            room_type (str):
                Specify what sort of arena generation to use.
                    "sequential":
                        Results in rooms that are nested within one another. Subsequent rooms get progressively smaller.
                    "parallel"
                        Results in rooms that are NOT nested within one another.
                        Ideally use num_rooms=3
                    "quadrant"
                        Results in a single room that is randomly placed in the corner of the play arena.
            gen_blocks (bool):
                Specify if the mission should randomly generate blocks for the agents to pick up and place.
            num_blocks (int):
                Specify the number of blocks that should be generated.
            gen_stairs (bool):
                Specify if the mission should randomly generate stairs for the agents to pick up and place.
            num_stairs (int):
                Specify the number of stairs that should be generated.


            These keyword arguments are only valid when using room_type="sequential" or room_type="parallel".
                num_rooms (int):
                    Specify the number of rooms to divide the arena into. The doors in between rooms will be randomly placed. If is_open_arena=True, the walls creating the rooms will still generate but will act as obstacles instead.


            These keyword arguments are only valid when using room_type="quadrant".
                quadrant_size (int):
                    Specify the size of the quadrant room. Will result in a room of size quadrant_size * quadrant_size.
                    Defaults to randint(4, arena_size // 2).
                quadrant_loc (int):
                    Specify which corner to place the quadrant room. Defaults to randint(0, 3).
                    0 1
                    2 3
                quadrant_num_doors (int):
                    Specify how many doors the quadrant room should have. Defaults to randint(1, 2).
                    1 - A door will be randomly placed one of the walls
                    2 - A door will be placed on both walls

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
    # process extra settings regarding room generation
    if "num_rooms" in kwargs:
        num_rooms = kwargs["num_rooms"]
        if type(num_rooms) == tuple:
            num_rooms = randint(*num_rooms)
    else:
        num_rooms = 0

    # 2D map of PLAY AREA
    play_arena = [[0 for _ in range(arena_size)] for _ in range(arena_size)]

    # tracks ROW INDEX doors for vertical walls and COL INDEX doors for horizontal walls to prevent walls from intersecting each other at doorways
    vertical_doors = []
    horizontal_doors = []

    # divider placement will always flip every other divider
    last_was_horizontal = True

    # generate dividers/obstacles
    if num_rooms > 1:
        room_count = 0
        if kwargs["room_type"] == "sequential":
            while room_count != num_rooms - 1:
                # don't want to place dividers against the outer walls
                # determines what row or column a divider will start
                wall_index = randint(3, arena_size - 4)

                # vertical divider
                if last_was_horizontal:
                    # retry placement of vertical divider as it would've gone in a door of a horizontal divider
                    if wall_index in horizontal_doors:
                        continue

                    # start divider from top
                    if randint(-1, 0) > 0:
                        for i in range(arena_size):
                            # generation of this divider bumped into another divider
                            if play_arena[i][wall_index] == 1:
                                break
                            play_arena[i][wall_index] = 1

                        # create door within divider
                        door_index = randint(0, i - 1)
                        play_arena[door_index][wall_index] = 0

                    # start divider from bottom
                    else:
                        for i in range(arena_size - 1, -1, -1):
                            # generation of this divider bumped into another divider
                            if play_arena[i][wall_index] == 1:
                                break
                            play_arena[i][wall_index] = 1

                        # create door within divider
                        door_index = randint(i, arena_size - 1)
                        play_arena[door_index][wall_index] = 0

                    vertical_doors.append(door_index)

                # horizontal divider
                else:
                    # retry placement of horizontal divider as it would've gone in a door of a vertical divider
                    if wall_index in vertical_doors:
                        continue

                    # start divider from left
                    if randint(-1, 0) < 0:
                        for i in range(arena_size):
                            # generation of this divider bumped into another divider
                            if play_arena[wall_index][i] == 1:
                                break
                            play_arena[wall_index][i] = 1

                        # create door within divider
                        door_index = randint(0, i - 1)
                        play_arena[wall_index][door_index] = 0

                    # start divider from right
                    else:
                        for i in range(arena_size - 1, -1, -1):
                            # generation of this divider bumped into another divider
                            if play_arena[wall_index][i] == 1:
                                break
                            play_arena[wall_index][i] = 1

                        # create door within divider
                        door_index = randint(i + 1, arena_size - 1)
                        play_arena[wall_index][door_index] = 0

                    horizontal_doors.append(door_index)

                last_was_horizontal = not last_was_horizontal

                room_count += 1
        elif kwargs["room_type"] == "parallel":
            while room_count != num_rooms - 1:
                # don't want to place dividers against the outer walls
                # determines what row or column a divider will start
                wall_index = randint(3, arena_size - 4)

                # vertical divider
                if last_was_horizontal:
                    # retry placement of vertical divider as it would've gone in a door of a horizontal divider
                    if wall_index in horizontal_doors:
                        continue

                    # start divider from top
                    if randint(-1, 0) > 0:
                        for i in range(arena_size):
                            # generation of this divider bumped into another divider
                            if play_arena[i][wall_index] == 1:
                                break
                            play_arena[i][wall_index] = 1

                        # create door within divider
                        door_index = randint(0, i - 1)
                        play_arena[door_index][wall_index] = 0

                    # start divider from bottom
                    else:
                        for i in range(arena_size - 1, -1, -1):
                            # generation of this divider bumped into another divider
                            if play_arena[i][wall_index] == 1:
                                break
                            play_arena[i][wall_index] = 1

                        # create door within divider
                        door_index = randint(i, arena_size - 1)
                        play_arena[door_index][wall_index] = 0

                    vertical_doors.append(door_index)

                # horizontal divider
                else:
                    # retry placement of horizontal divider as it would've gone in a door of a vertical divider
                    if wall_index in vertical_doors:
                        continue

                    # start divider from left
                    if randint(-1, 0) < 0:
                        for i in range(arena_size):
                            # generation of this divider bumped into another divider
                            if play_arena[wall_index][i] == 1:
                                bumped_wall_col_index = i
                                break
                            play_arena[wall_index][i] = 1

                        # create door within new divider
                        door_index = randint(0, i - 1)
                        play_arena[wall_index][door_index] = 0

                        # create door within old bumped divider
                        try:
                            bumped_wall_row_index = [
                                row[bumped_wall_col_index] for row in play_arena
                            ].index(0)

                            # new door top
                            if bumped_wall_row_index > wall_index:
                                row = randint(0, wall_index - 1)
                                col = bumped_wall_col_index
                                play_arena[row][col] = 0
                            # new door bottom
                            else:
                                row = randint(wall_index + 1, arena_size - 1)
                                col = bumped_wall_col_index
                                play_arena[row][col] = 0
                        except:
                            pass

                    # start divider from right
                    else:
                        for i in range(arena_size - 1, -1, -1):
                            # generation of this divider bumped into another divider
                            if play_arena[wall_index][i] == 1:
                                bumped_wall_col_index = i
                                break
                            play_arena[wall_index][i] = 1

                        # create door within new divider
                        door_index = randint(i + 1, arena_size - 1)
                        play_arena[wall_index][door_index] = 0

                        # create door within old bumped divider
                        try:
                            bumped_wall_row_index = [
                                row[bumped_wall_col_index] for row in play_arena
                            ].index(0)

                            # new door top
                            if bumped_wall_row_index > wall_index:
                                row = randint(0, wall_index - 1)
                                col = bumped_wall_col_index
                                play_arena[row][col] = 0
                            # new door bottom
                            else:
                                row = randint(wall_index + 1, arena_size - 1)
                                col = bumped_wall_col_index
                                play_arena[row][col] = 0
                        except:
                            pass

                    horizontal_doors.append(door_index)

                last_was_horizontal = not last_was_horizontal

                room_count += 1
        elif kwargs["room_type"] == "quadrant":
            # determine location of quadrant room
            # 0 1
            # 2 3
            room_loc = randint(0, 3)

            # determine size of quadrant room
            room_size = randint(4, arena_size // 2)

            # determine number of doors in quadrant room
            num_doors = randint(1, 2)

            # top left quadrant room
            if room_loc == 0:
                # create quadrant room
                mission_string += f"""
                    <DrawCuboid x1='0' y1='2' z1='0' x2='{room_size}' y2='2' z2='{room_size}' type='cobblestone'/>
                    <DrawCuboid x1='0' y1='2' z1='0' x2='{room_size - 1}' y2='2' z2='{room_size - 1}' type='air'/>"""

                # track quadrant play area
                # (top_left, bottom_right)
                quadrant_coords = ((0, 0), (room_size - 1, room_size - 1))

                # create doors
                # randomize placement of ONE door
                if num_doors == 1:
                    # horizontal wall
                    door_index = randint(quadrant_coords[0][0], quadrant_coords[1][1])
                    if randint(-1, 0) < 0:
                        mission_string += f"""
                            <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    else:
                        mission_string += f"""
                            <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
                # create doors on both walls
                else:
                    # horizontal wall
                    door_index = randint(quadrant_coords[0][0], quadrant_coords[1][1])
                    mission_string += f"""
                            <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    door_index = randint(quadrant_coords[0][0], quadrant_coords[1][1])
                    mission_string += f"""
                            <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
            # top right quadrant room
            elif room_loc == 1:
                # create quadrant room
                mission_string += f"""
                    <DrawCuboid x1='{arena_size - 1} 'y1='2' z1='0' x2='{room_size}' y2='2' z2='{room_size}' type='cobblestone'/>
                    <DrawCuboid x1='{arena_size - 1}' x2='{room_size + 1}' y1='2' y2='2' z1='0' z2='{room_size - 1}' type='air'/>"""

                # track quadrant play area
                # (top right, bottom left)
                quadrant_coords = ((0, arena_size - 1), (room_size - 1, room_size + 1))

                # create doors
                # randomize placement of ONE door
                if num_doors == 1:
                    # horizontal wall
                    if randint(-1, 0) < 0:
                        door_index = randint(
                            quadrant_coords[1][1], quadrant_coords[0][1]
                        )
                        mission_string += f"""
                            <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    else:
                        door_index = randint(
                            quadrant_coords[0][0], quadrant_coords[1][0]
                        )
                        mission_string += f"""
                            <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
                # create doors on both walls
                else:
                    # horizontal wall
                    door_index = randint(quadrant_coords[1][1], quadrant_coords[0][1])
                    mission_string += f"""
                        <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                    mission_string += f"""
                        <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
            # bottom left quadrant room
            elif room_loc == 2:
                # create quadrant room
                mission_string += f"""
                    <DrawCuboid x1='0' y1='2' z1='{arena_size - 1}' x2='{room_size}' y2='2' z2='{room_size}' type='cobblestone'/>
                    <DrawCuboid x1='0' y1='2' z1='{arena_size - 1}' x2='{room_size - 1}' y2='2' z2='{room_size + 1}' type='air'/>"""

                # track quadrant play area
                # (top right, bottom left)
                quadrant_coords = ((room_size + 1, room_size - 1), (arena_size - 1, 0))

                # create doors
                # randomize placement of ONE door
                if num_doors == 1:
                    # horizontal wall
                    if randint(-1, 0) < 0:
                        door_index = randint(
                            quadrant_coords[1][1], quadrant_coords[0][1]
                        )
                        mission_string += f"""
                            <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    else:
                        door_index = randint(
                            quadrant_coords[0][0], quadrant_coords[1][0]
                        )
                        mission_string += f"""
                            <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
                # create doors on both walls
                else:
                    # horizontal wall
                    door_index = randint(quadrant_coords[1][1], quadrant_coords[0][1])
                    mission_string += f"""
                        <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                    mission_string += f"""
                        <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
            # bottom right quadrant room
            elif room_loc == 3:
                # create quadrant room
                mission_string += f"""
                    <DrawCuboid x1='{arena_size - 1}' y1='2' z1='{arena_size - 1}' x2='{room_size}' y2='2' z2='{room_size}' type='cobblestone'/>
                    <DrawCuboid x1='{arena_size - 1}' y1='2' z1='{arena_size - 1}' x2='{room_size + 1}' y2='2' z2='{room_size + 1}' type='air'/>"""

                # track quadrant play area
                # (top left, bottom right)
                quadrant_coords = (
                    (room_size + 1, room_size + 1),
                    (arena_size - 1, arena_size - 1),
                )

                # create doors
                # randomize placement of ONE door
                if num_doors == 1:
                    # horizontal wall
                    if randint(-1, 0) < 0:
                        door_index = randint(
                            quadrant_coords[0][1], quadrant_coords[1][1]
                        )
                        mission_string += f"""
                            <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    else:
                        door_index = randint(
                            quadrant_coords[0][0], quadrant_coords[1][0]
                        )
                        mission_string += f"""
                            <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
                # create doors on both walls
                else:
                    # horizontal wall
                    door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
                    mission_string += f"""
                        <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

                    # vertical wall
                    door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                    mission_string += f"""
                        <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""

        else:
            print(kwargs["room_type"])
            raise ValueError(f"room_type: {kwargs['room_type']} is not supported.")

    # place dividers based on 2D map of play area
    for row_index in range(len(play_arena)):
        for col_index in range(len(play_arena)):
            if play_arena[row_index][col_index] == 1:
                mission_string += f"""
                    <DrawBlock x='{col_index}'  y='{2}' z='{row_index}' type='cobblestone'/>"""

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
        arena_size=10, is_closed_arena=True, num_rooms=3, room_type="quadrant"
    )
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
