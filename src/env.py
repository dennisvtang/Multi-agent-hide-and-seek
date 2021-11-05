from random import randint


def quadrant_env(
    arena_size: int,
    num_blocks: int,
    num_stairs: int,
    **kwargs,
):
    """
    Generates an environment where a room is randomly placed in a corner of the play area.

    Arguments:
        arena_size (int):
            Specify the size of the square play area for the agents. Resulting play area will be of size (arena_size * arena_size). Does not include the walls of the arena.
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

    # determine size of quadrant room
    if "quadrant_size" in kwargs:
        quadrant_size = kwargs["quadrant_size"]
    else:
        quadrant_size = randint(4, arena_size // 2)

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

    # generate quadrant room
    if quadrant_loc == 0:
        # create top left quadrant room
        quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='0' x2='{quadrant_size}' y2='2' z2='{quadrant_size}' type='cobblestone'/>
                    <DrawCuboid x1='0' y1='2' z1='0' x2='{quadrant_size - 1}' y2='2' z2='{quadrant_size - 1}' type='air'/>"""

        # track quadrant play area
        # (top_left, bottom_right)
        quadrant_coords = ((0, 0), (quadrant_size - 1, quadrant_size - 1))

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # horizontal wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][1])
            if randint(-1, 0) < 0:
                quadrant_env += f"""
                    <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            else:
                quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
        # create doors on both walls
        else:
            # horizontal wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][1])
            quadrant_env += f"""
                    <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][1])
            quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
    elif quadrant_loc == 1:
        # create top right quadrant room
        quadrant_env += f"""
                    <DrawCuboid x1='{arena_size - 1} 'y1='2' z1='0' x2='{quadrant_size}' y2='2' z2='{quadrant_size}' type='cobblestone'/>
                    <DrawCuboid x1='{arena_size - 1}' x2='{quadrant_size + 1}' y1='2' y2='2' z1='0' z2='{quadrant_size - 1}' type='air'/>"""

        # track quadrant play area
        # (top right, bottom left)
        quadrant_coords = ((0, arena_size - 1), (quadrant_size - 1, quadrant_size + 1))

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[1][1], quadrant_coords[0][1])
                quadrant_env += f"""
                    <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
        # create doors on both walls
        else:
            # horizontal wall
            door_index = randint(quadrant_coords[1][1], quadrant_coords[0][1])
            quadrant_env += f"""
                <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            quadrant_env += f"""
                <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
    elif quadrant_loc == 2:
        # create bottom left quadrant room
        quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='{arena_size - 1}' x2='{quadrant_size}' y2='2' z2='{quadrant_size}' type='cobblestone'/>
                    <DrawCuboid x1='0' y1='2' z1='{arena_size - 1}' x2='{quadrant_size - 1}' y2='2' z2='{quadrant_size + 1}' type='air'/>"""

        # track quadrant play area
        # (top right, bottom left)
        quadrant_coords = ((quadrant_size + 1, quadrant_size - 1), (arena_size - 1, 0))

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[1][1], quadrant_coords[0][1])
                quadrant_env += f"""
                    <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
        # create doors on both walls
        else:
            # horizontal wall
            door_index = randint(quadrant_coords[1][1], quadrant_coords[0][1])
            quadrant_env += f"""
                <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            quadrant_env += f"""
                <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
    elif quadrant_loc == 3:
        # create bottom right quadrant room
        quadrant_env += f"""
                    <DrawCuboid x1='{arena_size - 1}' y1='2' z1='{arena_size - 1}' x2='{quadrant_size}' y2='2' z2='{quadrant_size}' type='cobblestone'/>
                    <DrawCuboid x1='{arena_size - 1}' y1='2' z1='{arena_size - 1}' x2='{quadrant_size + 1}' y2='2' z2='{quadrant_size + 1}' type='air'/>"""

        # track quadrant play area
        # (top left, bottom right)
        quadrant_coords = (
            (quadrant_size + 1, quadrant_size + 1),
            (arena_size - 1, arena_size - 1),
        )

        # create doors
        # randomize placement of ONE door
        if quadrant_num_doors == 1:
            # horizontal wall
            if randint(-1, 0) < 0:
                door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
                quadrant_env += f"""
                    <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            else:
                door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
                quadrant_env += f"""
                    <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""
        # create doors on both walls
        else:
            # horizontal wall
            door_index = randint(quadrant_coords[0][1], quadrant_coords[1][1])
            quadrant_env += f"""
                <DrawCuboid x1='{door_index}' y1='2' z1='0' x2='{door_index}' y2='2' z2='{arena_size - 1}' type='air'/>"""

            # vertical wall
            door_index = randint(quadrant_coords[0][0], quadrant_coords[1][0])
            quadrant_env += f"""
                <DrawCuboid x1='0' y1='2' z1='{door_index}' x2='{arena_size - 1}' y2='2' z2='{door_index}' type='air'/>"""

    # TODO generate blocks
    if num_blocks != 0:
        pass

    # TODO generate stairs
    if num_stairs != 0:
        pass

    return quadrant_env


def create_env(
    arena_size: int,
    is_closed_arena: bool,
    env_type: str,
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
        env += quadrant_env(
            arena_size=arena_size,
            num_blocks=num_blocks,
            num_stairs=num_stairs,
            **kwargs,
        )
    elif env_type == "sequential":
        pass
    elif env_type == "parallel":
        pass
    else:
        raise ValueError(f"room_type: {env_type} is not supported.")

    env += """
                </DrawingDecorator>"""

    return env


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
