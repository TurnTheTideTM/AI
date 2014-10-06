'''
Created on 06.10.2014

@author: Andreas_2
'''

from pybrain.rl.environments import EpisodicTask
from pybrain.rl.environments import Environment
from PlanetEnvironment import environment_client

INDEX_FUNDS = 0
INDEX_TROUPS = 1
INDEX_MODE = 2
INDEX_PROD = 3
INDEX_SURR = 4

class episodic_planet_task(EpisodicTask):
    
    score_before = 0

    def __init__(self, planetEnv):
        self.discount = 0
        self.env = planetEnv
        
    def isFinished(self):
        planet_environment.is_finished()
        
    def getReward(self):
        score_now = self.score_before+self.evaluate_score(self.env.state)
        difference = score_now-self.score_before
        self.score_before = score_now
        return difference
    
    def evaluate_score(self,state):
        return 0
    
    def reset(self):
        EpisodicTask.reset(self)
        self.score_before = 0
    
class planet_environment(environment_client, Environment):
    nextMove = (0,0,0)
    state = None
    def __init__(self):
        pass
    
    def is_finished(self):
        #Use of index 0...
        return self.state[INDEX_FUNDS] != 0
    
    def getSensors(self):
        return self.state
    
    def performAction(self, action):
        assert len(action) == 3
        if(action[0] >= 0 and action[0]<4):
            self.nextMove = action
        else:
            self.nextMove = (0,0,0)
        
    def ask_next_move(self):
        return self.nextMove
    
    def give_next_state(self, state):
        self.state = state
        
    def reset(self):
        self.nextMove = (0,0,0)
        self.state = None
        

