"""
keyboardAgents.py
"""
import pygame
import random
import sys
from game import Agent
from game import Directions

class KeyboardAgent(Agent):
    """
    An agent controlled by the keyboard.
    """

    def __init__(self, index = 0):
        self.lastMove = Directions.STOP
        self.index = index
        self.keys = []

    def getAction(self, state, agentStateIndex):

        keys = pygame.key.get_pressed()
        if keys!=[]:
            self.keys = keys

        legal = state.getLegalActions(agentStateIndex)
        move = self.getMove()

        if(move not in legal):
            move = Directions.STOP
        
        self.lastMove = move
        return move

    def getMove(self):
        move = Directions.STOP
        if (self.keys[pygame.K_LEFT]): move = Directions.LEFT
        if (self.keys[pygame.K_RIGHT]): move = Directions.RIGHT
        if (self.keys[pygame.K_SPACE]): move = Directions.FIRE
        return move