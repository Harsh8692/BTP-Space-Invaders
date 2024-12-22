"""
BulletAgent.py
"""
from game import Agent, Directions
import util

class Bullet(Agent):

    def __init__(self, index):
        self.index = index

    def getAction(self, state, agentIndex): 
        util.raiseNotDefined()
    
# up bullets only move in UP direction
class UpBulletAgent(Bullet):

    def getAction(self, state, agentIndex): 
        return Directions.UP
    
# down bullets only move in DOWN direction
class DownBulletAgent(Bullet):

    def getAction(self, state, agentIndex): 
        return Directions.DOWN