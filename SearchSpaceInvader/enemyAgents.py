"""
enemyAgent.py
"""

from game import Agent, Directions, Actions
import util
import random
from util import manhattanDistance, semiManhattanDistance

# Enemy Agent as child class of Agent. It is used to get actions for enemies based on some distribution.
class EnemyAgent( Agent ):
    def __init__(self, index):
        self.index = index

    def getAction(self, state, agentIndex): 
        dist = self.getDistribution(state, agentIndex)
        if len(dist) == 0:
            return Directions.STOP
        else:
            return util.chooseFromDistribution(dist)

    def getDistribution(self, state, agentIndex):
        util.raiseNotDefined()


# random enemy agent 
class RandomAgent(EnemyAgent):

    def getDistribution(self, state, agentIndex):
        dist = util.Counter()
        for a in state.getLegalActions(agentIndex):
            if a==Directions.FIRE:
                dist[a] = 0.5 # this makes sures enemy does not fires as frequently as its other actions
            else: dist[a] = 1.0

        dist.normalize()
        return dist


# it is a directional agent which moves towards the spaceship
class DirectionalAgent(EnemyAgent):

    def __init__(self, index, probAttack=0.8):
        self.index = index
        self.probAttack = probAttack

    def getDistribution(self, state, agentIndex):
        
        legalActions = state.getLegalActions(agentIndex)
        pos = state.getEnemyPosition(agentIndex)

        speed = 1

        actionVectors = [Actions.actionToVector(a, speed) for a in legalActions]
        newPositions = [(pos[0]+a[0][0], pos[1]+a[0][1]) for a in actionVectors]
        spaceshipPosition = state.getSpaceShipPosition()

        distancesToSpaceShip = [manhattanDistance(pos, spaceshipPosition) for pos in newPositions]

        bestScore = float("inf")
        for i in range(len(distancesToSpaceShip)):
            if distancesToSpaceShip[i] and bestScore > distancesToSpaceShip[i]:
                bestScore = distancesToSpaceShip[i]
        
        bestProb = self.probAttack

        bestActions = [action for action, distance in zip(legalActions, distancesToSpaceShip) if distance==bestScore]

        dist = util.Counter()
        for a in bestActions:
            dist[a] = bestProb / len(bestActions)
        for a in legalActions:
            dist[a] += (1-bestProb) / len(legalActions)
        dist.normalize()
        return dist