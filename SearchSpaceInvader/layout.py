"""
For different layouts of the game
"""
import copy
from util import *
from game import Grid
import pygame
from queue import Queue
import math


class Layout:
    """
    A Layout manages the static information about the game board.
    """

    def __init__(self, layoutText):
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.agentPositions = []
        self.numEnemies = 0
        self.asteroid = Grid(self.width, self.height, False)
        self.processLayoutText(layoutText)
        self.enemies = []
        self.layoutText = layoutText
        self.totalAsteroid = len(self.asteroid.asList())

    def getNumEnemies(self):
        return self.numEnemies  
    
    def isWall(self, pos):
        x, y = pos
        return self.walls[x][y]
    

    def getRandomCorner(self):
        poses = [(1,1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def getFurthestCorner(self, spPos):
        poses = [(1,1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        dist, pos = max([(manhattanDistance(p, spPos), p) for p in poses])
        return pos
    
    def getEnemies(self):
        self.enemies = [(i, pos) for i, j, k, pos in self.agentPositions if i==0 and j==0 and k==0]
        return self.enemies

    def __str__(self):
        return "\n".join(self.layoutText)

    def deepCopy(self):
        return Layout(self.layoutText[:])
    
    def processLayoutText(self, layoutText):
        """
        Coordinates are flipped from the input format to the (x,y) convention here

        The shape of the maze. Each character
        represents a different type of object.
         % - Wall
         F - Asteroid
         E - Enemy
         S - SpaceShip
        Other characters are ignored.
        """
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[y][x]
                self.processLayoutChar(x, y, layoutChar)

        self.agentPositions.sort()
        self.agentPositions = [ ( i == 0, i>self.numEnemies, i>self.numEnemies, pos ) for i, pos in self.agentPositions] 

    def processLayoutChar(self, x, y, layoutChar):
        if layoutChar == 'S':
            self.agentPositions.append( (0, (x, y) ) )
        elif layoutChar == 'F':
            self.asteroid[x][y] = True
        elif layoutChar == 'E':
            self.agentPositions.append( (1, (x, y) ) )
            self.numEnemies += 1
        elif layoutChar == '%': 
            self.walls[x][y] = True 

def getLayout(filename):
    file_path = 'layouts/' + filename + '.lay'
    f = open(file_path)
    lines = [line.strip() for line in f]
    f.close()
    return Layout(lines)