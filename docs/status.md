---
layout: default
title: Status report
---


# Video Summary


# Project Summary


# Approach


# Evaluation
We evaluated the project by using a top down view through an observation agent that allows us to clearly see how the agents are moving and responding, along with any possible routes that either the seeker or hider can take to evaluate the effectiveness of their learning.

In our current iteration of the project, we utilized a simple reward system:


| Seeker Action  | Reward |
| ------------- | ------------- |
| Staring at sky  | - 1  |
| Catching hider (cursor collides with hider)  | + 5  |


| Hider Action  | Reward |
| ------------- | ------------- |
| Staring at sky  | - 1  |
| Getting caught (Seeker’s cursor collides with hider)  | - 5  |


Using this reward policy of +5 or -5 for the respective agents, the hider was able to effectively learn to how to avoid getting caught as long as possible and the seeker was able to learn tactics to quickly search the entire arena for the hider. However, the hider agent was able to improve faster than the seeker agent and learned to place dirt blocks at the open door locations in order to block themselves off into a subsection of the arena so the seeker could not reach them. The seeker was provided a shovel that allowed them to break the dirt blocks, but they struggled to figure out to achieve that in order to reach the blocked off hider. 

<p align="center">
  <img src="./res/hider_blocked_off.png">
</p>

Lastly, after evaluating the reinforcement learning for both agents, the staring at the sky penalty was included because we realized that we wanted to discourage the agents from observing unimportant areas outside of the mission space in order to streamline the learning process.




# Remaining Goals and Challenges

One of the remaining goals and challenges for our model is implementing the actual multi-agent aspect. Although our current iteration of this project is simply in the proof of concept stage for multi-agent reinforcement learning, we are confident that it is something achievable with Malmo. Currently we have the project set up in such a way that one agent will train until the mission ends, and subsequently, the second agent will begin training. This continues alternating back and forth so essentially, only one agent is actually training and learning at a time while the other does nothing in order to prevent the hider’s and seeker’s rewards from contradicting each other. However, we believe we will be able to just take the two respective agents and dump them into the multi-agent framework so they can both run concurrently while avoiding the issue with the contradictory rewards. After tinkering with the framework for some time, we do not anticipate that this challenge will cause too many issues and is definitely a goal that can feasibly be achieved by the final report. 

Another goal that we had in mind for this project was to incorporate multiple agents for both the seekers and hiders. Currently, we are only limiting our scope to one seeker and one hider in order to simplify and streamline the implementation process. After we are able to get the previous goal of having the seeker and hider train simultaneously through separate models, we can begin looking into expanding and tinkering with the number of agents hiding and number of agents seeking for a mission. If either the seekers or the hiders are not having much success with the reinforcement learning, we can tweak the number of hiders or seekers available in the mission to make the task harder or easier and help guide the learning process in the right direction. 



# Resources Used
