try:
    from malmo import MalmoPython
except:
    import MalmoPython

import sys
import time
import uuid
import gym, ray
from gym.spaces import Box
import random

NUM_AGENTS = 2
if len(sys.argv) > 1:
    NUM_AGENTS = sys.argv[1]


def seeker_name(num):
    return "Seeker " + str(num)

def safeStartMission(agent_host, my_mission, my_client_pool, my_mission_record, role, expId):
    used_attempts = 0
    max_attempts = 5
    print("Calling startMission for role", role)
    while True:
        try:
            # Attempt start:
            agent_host.startMission(my_mission, my_client_pool, my_mission_record, role, expId)
            break
        except MalmoPython.MissionException as e:
            errorCode = e.details.errorCode
            if errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_WARMING_UP:
                print("Server not quite ready yet - waiting...")
                time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_INSUFFICIENT_CLIENTS_AVAILABLE:
                print("Not enough available Minecraft instances running.")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait in case they are starting up.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_NOT_FOUND:
                print("Server not found - has the mission with role 0 been started yet?")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait and retry.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            else:
                print("Other error:", e.message)
                print("Waiting will not help here - bailing immediately.")
                exit(1)
        if used_attempts == max_attempts:
            print("All chances used up - bailing now.")
            exit(1)
    print("startMission called okay.")

def safeWaitForStart(agent_hosts):
    print("Waiting for the mission to start", end=' ')
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 120  # Allow a two minute timeout.
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print(e.text)
            print("Bailing now.")
            exit(1)
        time.sleep(0.1)
        print(".", end=' ')
    if time.time() - start_time >= time_out:
        print("Timed out while waiting for mission to start - bailing.")
        exit(1)
    print()
    print("Mission has started.")


def get_mission_xml():
    xml = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                <About>
                    <Summary>Hide and Seek</Summary>
                </About>

                <ServerSection>
                    <ServerInitialConditions>
                        <Time>
                            <StartTime>12000</StartTime>
                            <AllowPassageOfTime>false</AllowPassageOfTime>
                        </Time>
                        <Weather>clear</Weather>
                    </ServerInitialConditions>
                    <ServerHandlers>
                        <FlatWorldGenerator generatorString="3;7,2;1;"/>
                        <DrawingDecorator>
                           <DrawCuboid x1='-20' x2='20' y1='2' y2='2' z1='-20' z2='20' type='air'/>
                           <DrawCuboid x1='-20' x2='-20' y1='1' y2='1' z1='20' z2='20' type='stone'/>
                       </DrawingDecorator>
                       <ServerQuitFromTimeUp description="" timeLimitMs="50000"/>
                   </ServerHandlers>
                </ServerSection>
    '''

    # Create n agents
    for i in range(NUM_AGENTS):
      xml += '''<AgentSection mode="Survival">
        <Name>''' + seeker_name(i+1) + '''</Name>
        <AgentStart>
          <Placement x="''' + str(random.randint(-15,15)) + '''" y="2" z="''' + str(random.randint(-15,15)) + '''"/>
        </AgentStart>
        <AgentHandlers>
          <ContinuousMovementCommands turnSpeedDegs="360"/>
          <ChatCommands/>
          <MissionQuitCommands/>
          <ObservationFromNearbyEntities>
            <Range name="entities" xrange="40" yrange="2" zrange="40"/>
          </ObservationFromNearbyEntities>
          <ObservationFromRay/>
          <ObservationFromFullStats/>
          <ObservationFromGrid>
            <Grid name="floorAll">
              <min x="-2" y="-1" z="-2"/>
              <max x="2" y="0" z="2"/>
            </Grid>
          </ObservationFromGrid>
        </AgentHandlers>
      </AgentSection>'''

    # Observer Agent
    xml += '''<AgentSection mode="Spectator">
            <Name>Observer</Name>
            <AgentStart>
              <Placement x="0.5" y="25" z="0.5" pitch="90"/>
            </AgentStart>
            <AgentHandlers>
              <ContinuousMovementCommands turnSpeedDegs="360"/>
              <MissionQuitCommands/>
              <VideoProducer>
                <Width>640</Width>
                <Height>640</Height>
              </VideoProducer>
            </AgentHandlers>
          </AgentSection>'''

    xml += '</Mission>'

    return xml


if __name__ == "__main__":
    agent_hosts = [MalmoPython.AgentHost()]

    # Parse the command-line options:
    agent_hosts[0].addOptionalFlag("debug,d", "Display debug information.")
    agent_hosts[0].addOptionalIntArgument("agents,n", "Number of agents to use, including observer.", 3)

    try:
        agent_hosts[0].parse(sys.argv)
    except RuntimeError as e:
        print('ERROR:', e)
        print(agent_hosts[0].getUsage())
        exit(1)
    if agent_hosts[0].receivedArgument("help"):
        print(agent_hosts[0].getUsage())
        exit(0)

    DEBUG = agent_hosts[0].receivedArgument("debug")


    agent_hosts += [MalmoPython.AgentHost() for x in range(1, NUM_AGENTS + 1)]

    my_mission = MalmoPython.MissionSpec(get_mission_xml(), True)
    my_mission_record = MalmoPython.MissionRecordSpec()
    my_mission.requestVideo(800, 500)
    my_mission.setViewpoint(1)

    client_pool = MalmoPython.ClientPool()
    for port in range(10000, 10000 + NUM_AGENTS + 1):
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', port))

    experimentID = str(uuid.uuid4())

    for i in range(len(agent_hosts)):
        safeStartMission(agent_hosts[i], my_mission, client_pool, MalmoPython.MissionRecordSpec(), i, experimentID)

    safeWaitForStart(agent_hosts)
    time.sleep(1)

    for agent_host in agent_hosts:
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("\nError:", error.text)

    print()
    print("Mission running ", end=" ")

    action_space = Box(-1, 1, (2,))

    while world_state.is_mission_running:
        for i in range(NUM_AGENTS):
            action = action_space.sample()
            commands = [
                'move ' + str(action[0]),
                'turn ' + str(action[1]),
            ]
            for command in commands:
                agent_hosts[i].sendCommand(command)
                time.sleep(.2)

            world_state = agent_hosts[i].getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)

