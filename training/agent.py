import random 

def get_rand_action(obs):
    return random.choice([
        [0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,0],[0,1,1]
        ])