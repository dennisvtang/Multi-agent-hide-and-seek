---
layout: default
title: Proposal
---

# Summary of the Project
We are planning on developing a multi agent team-based hide and seek system. There will be two types of agents in our project. The first agent, **the hiders**, have the objective of trying to run away from the seekers and not get caught for as long as possible. The second agent, **the seekers**, have the objective of trying to find the hiders within a time limit. Both the hiders and seekers will have to navigate obstacles and will have available to them various of tools and blocks to help them in their objectives. To simplify the context, the arena will be relatively small, placing emphasis on what the seekers do as opposed to whether or not the seeker finds the hiders at all.

A seeker agent will have found a hider agent when the hider is within the seeker's field of view, emanating from its head. We may also add an extra requirement that the seeker must be within melee distance for a hider to be "found," depending on our findings during training.

We have yet to define how the agent will perceive the world: whether through a viewport mounted on the agent's head like normal Minecraft, or through other means.

# AI/ML Algorithms
We will use self-training reinforcement learning algorithms to encourage generations of seekers and hiders to play hide-and-seek better over time: hiders will be rewarded for the duration of time that passes as they remain hidden, and seekers will be rewarded for finding hiders in as little time as possible.

# Evaluation Plan
We want to evaluate the agents based on a mix of quantitatve and qualitative metrics. The quantitatve metrics would gauge basic competencies, such as whether or not agents are piloting their characters properly. The qualitative metrics would gauge the problem solving of the agents. Their actions over the course of the game should display a certain degree of logic if learning is occurring as a result of the algorithm.

## Quantitative Evaluation
The amount of time that passes during each game could be an indicator of relative competence between hiders and seekers. However, there are other quantitative metrics that could indicate learning progress. "Useful input" describes commands made by the AI that practically impact the situation, and it can be measured using objective statistics. One such statistic is the amount of movement inputs made vs. how much the character actually moves. An entirely random agent would pontentially make many movement commands that do not result in movement at all due to collisions.

Disparate generations can also be pitted against each other to gauge progress. For example, generation 45 hiders could be pitted against generation 120 seekers, and if progress is to be expected, then the seekers should find the hiders in a shorter amount of time.

## Qualitative Evaluation
In addition to evaluating both hiders and seekers by the amount of time that has passed, we also want to evalulate the agents on their apparent intelligence. There are many tools available in the Minecraft world, and making intelligent use of blocks, space, and obstacles corresponds to the improvement in the agents' abilities. Although analyzing the intelligence of the agents through their actions could be subjective, refinement in decision-making is easy to discern when beginning with random, unlearned behavior. After basic locomotion competencies are achieved, qualitative evaluation should reveal a problem-solving arms-race between the hiders and seekers.

## Appointment with Instructor
The appointment date is set for October 26 at 3:30pm.

