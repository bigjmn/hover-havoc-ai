from gymnasium.spaces import Box, Dict, Discrete, MultiBinary, MultiDiscrete

from game.game_logic import * 

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
                "color": Discrete(3)
            }
        ),
        "player_score": Discrete(3600),
        "opponent_score": Discrete(3600)
    }
)