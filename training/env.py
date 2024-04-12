from typing import Any
import gymnasium
from gymnasium.spaces import Box, Dict, Discrete, MultiBinary, MultiDiscrete
 
from game.game_logic import * 
import random 

obs_space = Dict(
    {
        "player_craft": Dict(
            {
                "position": Box(0, WIDTH, shape=(2,)),
                "velocity": Box(-5, 5, shape=(2,)),
                "angle": Box(0, 2*math.pi, shape=())
            }
        ),
        "opponent_craft": Dict(
            {
                "position": Box(0, WIDTH, shape=(2,)),
                "velocity": Box(-5, 5, shape=(2,)),
                "angle": Box(0, 2*math.pi, shape=())
            }
        ),
        "ball": Dict(
            {
                "position": Box(0, WIDTH, shape=(2,)),
                "velocity": Box(-5, 5, shape=(2,)),
                
            }
        ),
        "posession": Discrete(3),
        "player_score": Discrete(3600),
        "opponent_score": Discrete(3600)
    }
)


class GameEnv(gymnasium.Env):
    def __init__(self, opponent_model):
        self.opponent_model = opponent_model 
        self.game = Game()

    def reset(self):
        self.game.reset_game()
        return self.game.observe_from("orange")
    
    def step(self, action):
        green_action = self.opponent_model(self.game.observe_from("green"))
        self.game.resolve_tick(action, green_action)
        obs = self.game.observe_from("orange")
        temp_reward = self.game.describe_posession("orange")
        reward = 0
        isOver, winner = self.game.check_termination()
        if isOver:
            reward = 1 if winner == "orange" else -1
        return obs, reward, isOver, False, temp_reward


