---
layout: default
title: Final report
---


# Video
<p align="center">
  <iframe width="560" height="315" src="https://www.youtube.com/embed/SwRPLrt1Y5A" frameborder="0" allow="accelerometer; autoplay;clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</p>

# Project Summary
The main objective of our project is to create a multi-agent Minecraft environment that encourages emergent, competitive behavior between two teams of agents: hiders and seekers. The hiders would be given 20 seconds to position themselves and place dirt blocks to avoid detection from seekers. The seekers would be given 20 seconds to detect the hiders by exploring the arena and digging up dirt blocks with an iron shovel. Detection is defined specifically as an event handler that fires when a ray casted from the center of an agent's viewport intersects with another agent's model. Training is done mainly through reinforcement learning self-play. <br/> <br/>

The arena is defined as the enclosed environment where the hiding and seeking between these two teams takes place. This arena is procedurally generated, with the main defining feature being an interior quadrant created by two walls within a square. The size of the arena and the interior quadrant is random, and gaps in the interior wall are placed to encourage the hider to block off certain sections of the arena. <br/> <br/>

For the starting baseline in our Malmo environment, the agents randomly wander around inside of the arena. The hider places its dirt in random positions around itself and does not move very far from its starting position. The seeker randomly swings its iron shovel and also does not move far from its starting position. The arena itself does not impact the behavior of the agents at the baseline. <br/> <br/>

Although some portions of this problem can be solved with deterministic algorithms given the various observation spaces we opted to try, both the hider and the seeker must evolve and adapt to the tactics of the opposing team in order to win. A deterministic algorithm is unable to evolve by definition, implying that if an opposing team utilizing a learning algorithm finds a local optimum to beat the deterministic algorithm, the deterministic algorithm would never be able to win again. In contrast, if a learning algorithm finds a local optimum to beat another learning algorithm, there is a chance that the losing learning algorithm can adjust to win again eventually. <br/> <br/>


# Approaches

Due to the limitations of Malmo, the toolset that we used to create the simulated environment, we explored six different environment schemes in an effort to work around limitations. The limitations are as follows: Malmo offers no built-in API for manually raycasting a viewport, each episode takes on average 1 minute and 30 seconds to resolve and rewards are consumed when more than one command is submitted per Minecraft tick. <br/><br/>

Our first approach was to utilize a vectorized Advantaged Actor-Critic (A2C) algorithm from the reinforcement framework StableBaselines 3. The observation space provided the agents access to information about the surrounding blocks in a 4 block radius, indicating which block was dirt, which block was air, and which block was a wall. We also incorporated facing information to the observation space as well, where we added degrees for both the pitch and yaw of the agent. Each agent would be compartmentalized as separate vector environments for the model to learn from. However, after implementation and preliminary testing, we learned that the hiders and seekers would provide contradictory rewards to the A2C algorithm, making it impossible to converge on local optimum. As our second approach, we shifted towards two A2C models, one per team of two agents, and a basic reward scheme where if any seeker detects any hider, the seekers would gain reward and the hiders would lose reward. No intelligent behavior was developed after 123,100 steps, with agents spending much of their turns staring into the sky or at the ground. <br/><br/>

We scaled back the complexity with our third approach, opting to provide each individual agent with a Soft Actor-Critic algorithm to power their decisions. We added raycast information to the observation space, notifying the agent if their cursor hovered over a dirt block, a wall block, or an agent block. Rewards would be the same, but we opted to train with one agent on each team instead of two. With the same rewards scheme, no intelligent behavior was developed in the seeker after 125,430 steps, but the hider started to occasionally place dirt blocks in gaps and around itself to prevent detection. Once again, agents spent a significant amount of time staring at the sky. We opted to add a penalty to agents for looking at the sky, since there was nothing relevant to the goals of the agents at that angle. After 96,780 steps, the agents spent a significant amount of time looking at the ground, and occasionally continued looking at the sky. <br/><br/>

Our fourth approach involved modifying the action space so that the agent was committed to 0.5 seconds of movement whenever issuing a command, to which it would zero out all of its movement parameters after finishing half a second of movement. We hoped that this would portray a more consistent observation/action space connection for the agent. We also removed the penalty for looking at the sky, since it seemed like this time commitment helped in preventing the agent from losing time trying to get to impossible viewport angles. After 101,100 steps with a particularly long step size due to the time commitment of each command, no intelligent behavior was developed. <br/><br/>

For our fifth approach, we expanded the reward spaces of the seeker by giving it a reward whenever it would explore a new cell in the arena. After 73,500 steps, this did not give any meaningful difference in behavior compared to previous approaches. For our sixth approach, we decided to augment the seeker's observation space with the distance to the closest hider. We hoped this would allow the seeker enough information to at least get close. After 98,100 steps, this was enough to develop what seemed to be a tendency for the seeker to advance towards the hider. <br/><br/>

In terms of comparative approach performance, we are unable to make any conclusions due to the most significant limitation of this project: the time it takes to simulate one step. Simulating 100,000 steps takes on average 16 hours to complete. According to a paper done by Open AI on Emergent Tool Use from Multi-Agent Autocurricula, they tackled a similar problem with a sparse reward scheme. Stage 4 progress, defined as consistent tool use, was only achieved in their reinforcement learning architecture after 100 million episodes using PPO, which took their hardware 34 hours to completely simulate. This would take us years given the simulation speed. To make matters worse, our reward scheme is even sparser compared to the one used in the Open AI paper, which would mean that we would need even more episodes because of our agent detection constraints. <br/><br/>

# Evaluation
Due to the sparse rewards of the scenario, quantitative evaluation through gradually increasing rewards like in class assignments is not possible. Instead, quantitative evaluation is better guided by the frequency of optimal rewards for indicators of performance of a given team. <br/><br/>

The hider team, which consisted of 1 agent for most iterations of the project, had optimal rewards at a frequency of 96% for all iterations. This was not because of intelligence on the hider's part; the problem that the hider needed to solve at a baseline is much simpler than the problem that the seeker needed to solve. Due to the seeker beginning with random decisions, the hider probabilistically had a much higher chance of winning than the seeker. <br/><br/>

The seeker team, which consisted of 1 agent for most iterations of the project, had optimal rewards at a frequency of 4% of all iterations except for the last iteration, which, over the course of 98,100 steps, improved to a frequency of 6%. The seeker team had an additional rewards scheme to encourage behavior that we believed would allow the seeker to find the hider more often; when we added the reward for new cells explored, an upward trend in overall reward totals was found, at about +0.4 points per 100 episodes. However, with our qualitative evaluations, this did not result in a higher level of apparent intelligent behavior. <br/><br/>

Qualitative evaluations in the first 4 iterations of the project lead us to rely on penalties to attempt to phase out the tendency for agents to stare directly into the sky. This resulted in the agents spending more time staring straight down into the ground. We were looking for the seeker in particular to scan with its cursor to detect dirt and explore the surrounding squares to find the hider. This behavior never emerged. Although the average distance between the hider and the seeker reduced by 0.4 blocks when we gave the seeker access to the distance to to the hider, the seeker never scanned its surroundings to find the hider, resulting in the seeker failing to find the hider even if the hider was adjacent to the seeker. <br/><br/>

In conclusion, although some minor improvements were found with the seeker, we did not succeed in finding productive workarounds to the limitations we had to encourage notable emergent behavior within the allotted time. Because the seeker could never consistently find the hider, the hider was never given a chance to develop a response. <br/><br/>
 


# References
Baker, Bowen, et al. “[1909.07528] Emergent Tool Use From Multi-Agent Autocurricula.” ArXiv.Org, arXiv, 11 Feb. 2020, https://arxiv.org/abs/1909.07528. <br/><br/>

---. “Emergent Tool Use from Multi-Agent Interaction.” OpenAI, OpenAI, 17 Sept. 2019, https://openai.com/blog/emergent-tool-use/. <br/><br/>

“Stable-Baselines3 Docs - Reliable Reinforcement Learning Implementations — Stable Baselines3 1.3.1a6 Documentation.” Stable-Baselines3 Docs - Reliable Reinforcement Learning Implementations — Stable Baselines3 1.3.1a6 Documentation, Read the Docs, 2021, https://stable-baselines3.readthedocs.io/en/master/. <br/><br/>
 
“XML Schema Documentation.” Microsoft on GitHub, 6 May 2019, https://microsoft.github.io/malmo/0.21.0/Schemas/MissionHandlers.html. <br/><br/>

