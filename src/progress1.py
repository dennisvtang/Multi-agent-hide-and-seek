class HideAndSeekMission(gym.Env):
    def __init__(self, env_config):
        ### Mission Parameters ###
        self.mission_xml = None #Use external arena generator for mission_xml
        ### END                ###


        ### Agent Parameters ###
        self.obs_size = 5
        self.num_agents = 2
        ### END              ###
        pass
    
    def reset(self):
        """
        Resets the environment for the next episode.

        Returns
            observation: <np.array> flattened initial obseravtion
        """
        pass

    def step(self, action):
        """
        Take an action in the environment and return the results.

        Args
            action: vector of actions taken from RL agent

        Returns
            observation: <np.array> flattened array of obseravtion
            reward: <int> reward from taking action
            done: <bool> indicates terminal state
            info: <dict> dictionary of extra information
        """
        pass
