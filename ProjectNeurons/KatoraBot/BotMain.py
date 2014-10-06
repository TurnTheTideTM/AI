'''
Created on 06.10.2014

@author: Andreas_2
'''

from pybrain.rl.environments import EpisodicTask
from pybrain.rl.environments import Environment
from PlanetEnvironment import environment_client
from pybrain.rl.agents.learning import LearningAgent
from pybrain.rl.learners.directsearch.enac import ENAC
from pybrain.structure.modules.neuronlayer import NeuronLayer
from pybrain.rl.experiments.experiment import Experiment
from pybrain.tools.shortcuts import buildNetwork

INDEX_FUNDS = 0
INDEX_TROUPS = 1
INDEX_MODE = 3
INDEX_PROD = 2
INDEX_SURR = 4

class episodic_planet_task(EpisodicTask):
    
    

    def __init__(self, planetEnv):
        self.discount = 0
        self.env = planetEnv
        self.score_before = 0
        
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
    

class planet_experiment(Experiment):
    
    def __init__(self):
        self.rewardID = 0
        super(planet_experiment, self).__init__()
        
    def _oneInteraction(self):
        self.stepid += 1
        self.agent.integrateObservation(self.task.getObservation())
        self.task.performAction(self.agent.getAction())


class planet_environment(environment_client, Environment):
    def __init__(self):
        self.nextMove = (0,0,0)
        self.state = None
        network = buildNetwork(9,100,3)
        enac_learner = ENAC()
        learning_agent = LearningAgent(network, enac_learner)
        self.experiment = planet_experiment(episodic_planet_task(self),learning_agent)
    
    def is_finished(self):
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
        self.experiment.doInteractions(1)
        
    def reset(self):
        self.nextMove = (0,0,0)
        self.state = None
        

