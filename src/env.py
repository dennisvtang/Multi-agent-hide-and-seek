from random import randint, choice
from typing import Dict


def gen_quadrant_env(
    arena_size: int,
    item_gen: Dict[str, bool],
    num_blocks: int,
    num_stairs: int,
    **kwargs,
):
    """
    Generates an environment where a room is randomly placed in a corner of the play area.

    Arguments:
        arena_size (int):
            Specify the size of the square play area for the agents. Resulting play area will be of size (arena_size * arena_size). Does not include the walls of the arena.
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
            Arbitrary keyword arguments.

    Supported **kwargs:
        quadrant_size (int):
            Specify the size of the quadrant room. Resulting play area of the room will be of size (quadrant_size * quadrant_size). This doesn't include the walls of the room.
            Defaults to randint(4, arena_size // 2).
        quadrant_loc (int):
            Specify which corner to place the quadrant room. Defaults to randint(0, 3).
            0 1
            2 3
        quadrant_num_doors (int):
            Specify how many doors the quadrant room should have. Defaults to randint(1, 2).
            1 - A door will be randomly placed one of the walls
            2 - A door will be placed on both walls
    """

    quadrant_env = ""
    
    # check if map has been provided
    if "play_arena" in kwargs:
        play_arena = kwargs["play_arena"]

        # place blocks based on 2D map
        for row_index in range(len(play_arena)):
            for col_index in range(len(play_arena)):
                if play_arena[row_index][col_index] == 1:
                    quadrant_env += f"""
                        <DrawBlock x='{col_index}'  y='{2}' z='{row_index}' type='cobblestone'/>
                        <DrawBlock x='{col_index}'  y='{3}' z='{row_index}' type='cobblestone'/>"""
        
        return (quadrant_env, play_arena)

    # determine size of quadrant room
    if "quadrant_size" in kwargs:
        if type(kwargs["quadrant_size"]) == tuple:
            quadrant_size = randint(*kwargs["quadrant_size"])
        else:
            quadrant_size = kwargs["quadrant_size"]
    else:
        quadrant_size = randint(3, arena_size // 2)

    # determine location of quadrant room
    # 0 1
    # 2 3
    if "quadrant_loc" in kwargs:
        quadrant_loc = kwargs["quadrant_loc"]
    else:
        quadrant_loc = randint(0, 3)

    # determine number of doors in quadrant room
    if "quadrant_num_doors" in kwargs:
        quadrant_num_doors = kwargs["quadrant_num_doors"]
    else:
        quadrant_num_doors = randint(1, 2)

    # todo make item_gen optional
    # todo allow choosing only some?
    # item_gen = dict(zip(item_gen, [choice([True, False]) for _ in range(4)]))

    # todo make num_blocks and num_stairs optional
    # todo make num_blocks accept ranges
    # todo make num_stairs accept ranges
    # determine if requested number of items is possible to spawn
    # generate items ANYWHERE
    if (
        item_gen["blocks_inside"]
        and item_gen["blocks_outside"]
        and item_gen["stairs_inside"]
        and item_gen["stairs_outside"]
    ):
        if (num_blocks + num_stairs) > (arena_size ** 2) - (
            (quadrant_size + 1) ** 2
        ) + (quadrant_size ** 2) + quadrant_num_doors:
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate items only INSIDE quadrant
    elif item_gen["blocks_inside"] and item_gen["stairs_inside"]:
        if (num_blocks + num_stairs) > (quadrant_size ** 2):
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate items only OUTSIDE quadrant
    elif item_gen["blocks_outside"] and item_gen["stairs_outside"]:
        if (num_blocks + num_stairs) > (arena_size ** 2) - (
            (quadrant_size + 1) ** 2
        ) + 2:
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate blocks ANYWHERE
    elif item_gen["blocks_inside"] and item_gen["blocks_outside"]:
        if num_blocks > (quadrant_size ** 2):
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate blocks INSIDE quadrant
    elif item_gen["blocks_inside"]:
        if (num_blocks) > (quadrant_size ** 2):
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate blocks OUTSIDE quadrant
    elif item_gen["blocks_outside"]:
        if num_blocks > (arena_size ** 2) - ((quadrant_size + 1) ** 2) + 2:
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate stairs ANYWHERE
    elif item_gen["stairs_inside"] and item_gen["stairs_outside"]:
        if num_stairs > (quadrant_size ** 2):
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate stairs INSIDE quadrant
    elif item_gen["stairs_inside"]:
        if num_stairs > (quadrant_size ** 2):
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )
    # generate stairs OUTSIDE quadrant
    elif item_gen["stairs_outside"]:
        if num_stairs > (arena_size ** 2) - ((quadrant_size + 1) ** 2) + 2:
            raise ValueError(
                f"Requested number of items to generate is larger than the space available in the selected area"
            )

    # 2D map of area agents can walk around
    # empty = 0
    # walls = 1
    # blocks = 2
    # stairs = 3
    # agents = 4
    play_arena = [[0 for _ in range(arena_size)] for _ in range(arena_size)]

    # generate quadrant room
    if quadrant_loc == 0:
        # create top left quadrant room
        # place horizontal wall
        for i in range(quadrant_size + 1):
            play_arena[quadrant_size][i] = 1
        # place vertical wall
        for i in range(quadrant_size + 1):
            play_arena[i][quadrant_size] = 1

        # top left, bottom right
        quadrant_coords = ((0, 0), (quadrant_size - 1, quadrant_size - 1))

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # place door on horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
                play_arena[quadrant_size][door_index] = 0
            # place door on vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                play_arena[door_index][quadrant_size] = 0
        # create doors on both walls
        else:
            # place door on horizontal wall
            door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
            play_arena[quadrant_size][door_index] = 0

            # place door on vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            play_arena[door_index][quadrant_size] = 0
    elif quadrant_loc == 1:
        # create top right quadrant room
        # place horizontal wall
        for i in range(arena_size - 1, arena_size - quadrant_size - 1, -1):
            play_arena[quadrant_size][i] = 1
        # place vertical wall
        for i in range(quadrant_size + 1):
            play_arena[i][arena_size - quadrant_size - 1] = 1

        # top left, bottom right
        quadrant_coords = (
            (0, arena_size - quadrant_size),
            (quadrant_size - 1, arena_size - 1),
        )

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # place door on horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
                play_arena[quadrant_size][door_index] = 0
            # place door on vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                play_arena[door_index][arena_size - quadrant_size - 1] = 0

        # create doors on both walls
        else:
            # place door on horizontal wall
            door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
            play_arena[quadrant_size][door_index] = 0

            # place door on vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            play_arena[door_index][arena_size - quadrant_size - 1] = 0
    elif quadrant_loc == 2:
        # create top right quadrant room
        # place horizontal wall
        for i in range(quadrant_size + 1):
            play_arena[arena_size - quadrant_size - 1][i] = 1
        # place vertical wall
        for i in range(arena_size - 1, arena_size - quadrant_size - 1, -1):
            play_arena[i][quadrant_size] = 1

        # top left, bottom right
        quadrant_coords = (
            (arena_size - quadrant_size, 0),
            (arena_size - 1, quadrant_size - 1),
        )

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # place door on horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
                play_arena[arena_size - quadrant_size - 1][door_index] = 0
            # place door on vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                play_arena[door_index][quadrant_size] = 0

        # create doors on both walls
        else:
            # place door on horizontal wall
            door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
            play_arena[arena_size - quadrant_size - 1][door_index] = 0

            # place door on vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            play_arena[door_index][quadrant_size] = 0
    elif quadrant_loc == 3:
        # create top right quadrant room
        # place horizontal wall
        for i in range(arena_size - 1, quadrant_size - 2, -1):
            play_arena[quadrant_size - 1][i] = 1
        # place vertical wall
        for i in range(arena_size - 1, quadrant_size - 2, -1):
            play_arena[i][quadrant_size - 1] = 1

        # top left, bottom right
        quadrant_coords = (
            (quadrant_size, quadrant_size),
            (arena_size - 1, arena_size - 1),
        )

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # place door on horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
                play_arena[quadrant_size - 1][door_index] = 0
            # place door on vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                play_arena[door_index][quadrant_size - 1] = 0

        # create doors on both walls
        else:
            # place door on horizontal wall
            door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
            play_arena[quadrant_size - 1][door_index] = 0

            # place door on vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            play_arena[door_index][quadrant_size - 1] = 0

    # place blocks based on 2D map
    for row_index in range(len(play_arena)):
        for col_index in range(len(play_arena)):
            if play_arena[row_index][col_index] == 1:
                quadrant_env += f"""
                    <DrawBlock x='{col_index}'  y='{2}' z='{row_index}' type='cobblestone'/>
                    <DrawBlock x='{col_index}'  y='{3}' z='{row_index}' type='cobblestone'/>"""

    # generate blocks
    if num_blocks != 0:
        block_counter = 0

        while block_counter != num_blocks:
            #! very lazy way of generating blocks
            block_index = (randint(0, arena_size - 1), randint(0, arena_size - 1))

            # generate blocks ANYWHERE in play area
            if item_gen["blocks_inside"] and item_gen["blocks_outside"]:
                # check if block would generate in a wall or another block
                if (
                    play_arena[block_index[0]][block_index[1]] == 1
                    or play_arena[block_index[0]][block_index[1]] == 2
                ):
                    continue
                else:
                    # mark where blocks have been placed
                    play_arena[block_index[0]][block_index[1]] = 2

                    # place block
                    quadrant_env += f"""
                    <DrawItem x="{block_index[1]}" y="2" z="{block_index[0]}" type="dirt"/>"""

            # generate blocks only INSIDE quadrant
            elif item_gen["blocks_inside"]:
                # check if block would've generate in a wall or existing block
                if (
                    play_arena[block_index[0]][block_index[1]] == 1
                    or play_arena[block_index[0]][block_index[1]] == 2
                ):
                    continue
                else:
                    # check if block would've generate OUTSIDE quadrant
                    if quadrant_loc == 0:
                        if (
                            block_index[0] > quadrant_coords[1][0]
                            or block_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 1:
                        if (
                            block_index[0] > quadrant_coords[1][0]
                            or block_index[1] < quadrant_coords[0][1]
                        ):
                            continue
                    elif quadrant_loc == 2:
                        if (
                            block_index[0] < quadrant_coords[0][0]
                            or block_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 3:
                        if (
                            block_index[0] < quadrant_coords[0][0]
                            or block_index[1] < quadrant_coords[0][1]
                        ):
                            continue

                    # mark where blocks have been placed
                    play_arena[block_index[0]][block_index[1]] = 2

                    # place blocks
                    quadrant_env += f"""
                    <DrawItem x="{block_index[1]}" y="2" z="{block_index[0]}" type="dirt"/>"""

            # generate blocks only OUTSIDE quadrant
            elif item_gen["blocks_outside"]:
                # check if block would've generate in a wall or existing block
                if (
                    play_arena[block_index[0]][block_index[1]] == 1
                    or play_arena[block_index[0]][block_index[1]] == 2
                ):
                    continue
                else:
                    # check if block would've generate INSIDE quadrant
                    if quadrant_loc == 0:
                        if not (
                            block_index[0] > quadrant_coords[1][0]
                            or block_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 1:
                        if not (
                            block_index[0] > quadrant_coords[1][0]
                            or block_index[1] < quadrant_coords[0][1]
                        ):
                            continue
                    elif quadrant_loc == 2:
                        if not (
                            block_index[0] < quadrant_coords[0][0]
                            or block_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 3:
                        if not (
                            block_index[0] < quadrant_coords[0][0]
                            or block_index[1] < quadrant_coords[0][1]
                        ):
                            continue

                    # mark where blocks have been placed
                    play_arena[block_index[0]][block_index[1]] = 2

                    # place blocks
                    quadrant_env += f"""
                    <DrawItem x="{block_index[1]}" y="2" z="{block_index[0]}" type="dirt"/>"""

            block_counter += 1

    # generate stairs
    if num_stairs != 0:
        stair_counter = 0

        while stair_counter != num_stairs:
            #! very lazy way of generating stairs
            stair_index = (randint(0, arena_size - 1), randint(0, arena_size - 1))

            # generate stairs ANYWHERE in play area
            if item_gen["stairs_inside"] and item_gen["stairs_outside"]:
                # check if stair would generate in a wall or another stair
                if (
                    play_arena[stair_index[0]][stair_index[1]] == 1
                    or play_arena[stair_index[0]][stair_index[1]] == 2
                    or play_arena[stair_index[0]][stair_index[1]] == 3
                ):
                    continue
                else:
                    # mark where stairs have been placed
                    play_arena[stair_index[0]][stair_index[1]] = 3

                    # place stair
                    quadrant_env += f"""
                    <DrawItem x="{stair_index[1]}" y="2" z="{stair_index[0]}" type="oak_stairs"/>"""

            # generate stairs only INSIDE quadrant
            elif item_gen["stairs_inside"]:
                # check if stair would've generate in a wall or existing stair
                if (
                    play_arena[stair_index[0]][stair_index[1]] == 1
                    or play_arena[stair_index[0]][stair_index[1]] == 2
                    or play_arena[stair_index[0]][stair_index[1]] == 3
                ):
                    continue
                else:
                    # check if stair would've generate OUTSIDE quadrant
                    if quadrant_loc == 0:
                        if (
                            stair_index[0] > quadrant_coords[1][0]
                            or stair_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 1:
                        if (
                            stair_index[0] > quadrant_coords[1][0]
                            or stair_index[1] < quadrant_coords[0][1]
                        ):
                            continue
                    elif quadrant_loc == 2:
                        if (
                            stair_index[0] < quadrant_coords[0][0]
                            or stair_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 3:
                        if (
                            stair_index[0] < quadrant_coords[0][0]
                            or stair_index[1] < quadrant_coords[0][1]
                        ):
                            continue

                    # mark where stairs have been placed
                    play_arena[stair_index[0]][stair_index[1]] = 3

                    # place stairs
                    quadrant_env += f"""
                    <DrawItem x="{stair_index[1]}" y="2" z="{stair_index[0]}" type="oak_stairs"/>"""

            # generate stairs only OUTSIDE quadrant
            elif item_gen["stairs_outside"]:
                # check if stair would've generate in a wall or existing stair
                if (
                    play_arena[stair_index[0]][stair_index[1]] == 1
                    or play_arena[stair_index[0]][stair_index[1]] == 2
                    or play_arena[stair_index[0]][stair_index[1]] == 3
                ):
                    continue
                else:
                    # check if stair would've generate INSIDE quadrant
                    if quadrant_loc == 0:
                        if not (
                            stair_index[0] > quadrant_coords[1][0]
                            or stair_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 1:
                        if not (
                            stair_index[0] > quadrant_coords[1][0]
                            or stair_index[1] < quadrant_coords[0][1]
                        ):
                            continue
                    elif quadrant_loc == 2:
                        if not (
                            stair_index[0] < quadrant_coords[0][0]
                            or stair_index[1] > quadrant_coords[1][1]
                        ):
                            continue
                    elif quadrant_loc == 3:
                        if not (
                            stair_index[0] < quadrant_coords[0][0]
                            or stair_index[1] < quadrant_coords[0][1]
                        ):
                            continue

                    # mark where stairs have been placed
                    play_arena[stair_index[0]][stair_index[1]] = 3

                    # place stairs
                    quadrant_env += f"""
                    <DrawItem x="{stair_index[1]}" y="2" z="{stair_index[0]}" type="oak_stairs"/>"""

            stair_counter += 1

    for i in play_arena:
        print(i)

    return (quadrant_env, play_arena)


def create_env(
    arena_size: int,
    is_closed_arena: bool,
    env_type: str,
    item_gen: Dict[str, bool],
    num_blocks: int,
    num_stairs: int,
    **kwargs,
):
    """
    Generates a formated Malmo mission XML string of the environment with the requested settings.

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
        str: A formated Malmo mission XML string of the environment.
    """

    env = ""

    # generate grass flat world
    env += f"""
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,2;1;"/>
                <DrawingDecorator>"""

    # reset blocks at arena
    env += f"""
                    <DrawCuboid x1='-1000' x2='1000' y1='1' y2='1' z1='-1000' z2='1000' type='grass'/>
                    <DrawCuboid x1='-1000' x2='1000' y1='2' y2='4' z1='-1000' z2='1000' type='air'/>"""

    # generate floor
    env += f"""
                    <DrawCuboid x1='0' x2='{arena_size - 1}' y1='1' y2='1' z1='0' z2='{arena_size - 1}' type='iron_block'/>"""

    # generate walls
    if is_closed_arena:
        env += f"""
                    <DrawCuboid x1='-1' x2='{arena_size}' y1='2' y2='3' z1='-1' z2='{arena_size}' type='stonebrick'/>
                    <DrawCuboid x1='0' x2='{arena_size - 1}' y1='2' y2='3' z1='0' z2='{arena_size - 1}' type='air'/>"""

    # generate environment
    if env_type == "quadrant":
        quadrant_env, env_map = gen_quadrant_env(
            arena_size=arena_size,
            item_gen=item_gen,
            num_blocks=num_blocks,
            num_stairs=num_stairs,
            **kwargs,
        )
        env += quadrant_env
    elif env_type == "sequential":
        pass
    elif env_type == "parallel":
        pass
    else:
        raise ValueError(f"room_type: {env_type} is not supported.")

    env += """
                </DrawingDecorator>"""

    return (env, env_map)


if __name__ == "__main__":
    print(
        create_env(
            arena_size=10,
            is_closed_arena=True,
            env_type="quadrant",
            num_blocks=5,
            num_stairs=3,
        )
    )
