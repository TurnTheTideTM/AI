'''
Created on 06.10.2014

@author: Andreas_2
'''

from pybrain.rl.environments import EpisodicTask
from pybrain.rl.environments import Environment
from PlanetEnvironment import environment_client
from pybrain.rl.agents.learning import LearningAgent
from pybrain.rl.learners.directsearch.enac import ENAC
from pybrain.rl.experiments.experiment import Experiment
from pybrain.tools.shortcuts import buildNetwork

INDEX_FUNDS = 0
INDEX_TROUPS = 1
INDEX_MODE = 3
INDEX_PROD = 2
INDEX_PLANETS = 4
INDEX_SURR = 5

INPUT_NEURON_COUNT = 9

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
        return state[INDEX_FUNDS]+state[INDEX_TROUPS]*100+state[INDEX_PLANETS]*1000
    
    def reset(self):
        EpisodicTask.reset(self)
        self.score_before = 0
    
class planet_experiment(Experiment):
    
    def __init__(self, episodic, learning):
        self.reward_id = -1
        super(planet_experiment, self).__init__(episodic, learning)
        
    def _oneInteraction(self):
        if(self.stepid > self.reward_id):
            return
        self.stepid += 1
        self.agent.integrateObservation(self.task.getObservation())
        self.task.performAction(self.agent.getAction())
        
    def follow_with_reward(self):
        assert self.stepid == self.reward_id+1
        reward = self.task.getReward()
        self.agent.giveReward(reward)
        self.reward_id+=1
        return reward

class planet_environment(environment_client, Environment):
    
    ai_count = 0
    
    def __init__(self):
        self.this_ai_count = planet_environment.ai_count
        planet_environment.ai_count+=1
        self.nextMove = (0,0,0)
        self.state = None
        network = buildNetwork(INPUT_NEURON_COUNT,100,3)
        enac_learner = ENAC()
        learning_agent = LearningAgent(network, enac_learner)
        self.experiment = planet_experiment(episodic_planet_task(self),learning_agent)
    
    def is_finished(self):
        return self.state[INDEX_FUNDS] != 0
    
    def getSensors(self):
        a = (self.state[:-1]+self.state[-1]) [:INPUT_NEURON_COUNT]
        a = a+(INPUT_NEURON_COUNT-len(a))*(0,)
    
    def performAction(self, action):
        assert len(action) == 3
        if(action[0] >= 0 and action[0]<4):
            action = (int(action[0]),int(action[1]),int(action[2]))
            self.nextMove = action
        else:
            self.nextMove = (0,0,0)
        
    def ask_next_move(self):
        self.experiment._oneInteraction()
        return self.nextMove
    
    def get_name(self):
        return "KatoraBot"+str(self.this_ai_count)
    
    def give_next_state(self, state):
        self.state = state
        if self.experiment.reward_id < 0:
            self.experiment.reward_id+=1
            return
        else:
            self.experiment.follow_with_reward()
        
    def reset(self):
        self.nextMove = (0,0,0)
        self.state = None
        

