---
layout: default
title: Status report
---


# Video Summary


# Project Summary


# Approach


# Evaluation


# Remaining Goals and Challenges

One of the remaining goals and challenges for our model is implementing the actual multi-agent aspect. Although our current iteration of this project is simply in the proof of concept stage for multi-agent reinforcement learning, we are confident that it is something achievable with Malmo. Currently we have the project set up in such a way that one agent will train until the mission ends, and subsequently, the second agent will begin training. This continues alternating back and forth so essentially, there are multiple agents in the environment but only one agent is actually training and learning at a time in order to prevent the hider’s and seeker’s rewards from contradicting each other. However, we believe we will be able to just take the two respective agents and dump them into the multi-agent framework so they can both run concurrently while avoiding the issue with contradictory rewards. After tinkering with the framework for some time, we do not anticipate that this challenge will cause too many issues and is definitely a goal that can feasibly be achieved by the final report. 

Another goal that we had in mind for this project was to incorporate multiple agents for both the seekers and hiders. Currently, we are only limiting our scope to one seeker and one hider in order to simplify and streamline the implementation process. After we are able to get the previous goal of having the seeker and hider train simultaneously through separate models, we can begin looking into expanding and tinkering with the number of agents hiding and number of agents seeking for a mission. If either the seekers or the hiders are not having much success with the reinforcement learning, we can tweak the number of hiders or seekers available in the mission to make the task harder or easier and help guide the learning process in the right direction. 



# Resources Used
