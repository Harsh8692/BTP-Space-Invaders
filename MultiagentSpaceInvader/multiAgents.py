from game import Agent
from spaceship import GameState
import random
from game import Game
import copy
from util import manhattanDistance, semiManhattanDistance
import util

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide. You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState: GameState, agentIndex):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState, agentIndex and returns
        some Directions.X for some X in the set {LEFT, RIGHT, FIRE, UP, DOWN, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions(agentIndex)

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (spaceship.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining asteroid (newAsteroid), new enemy states (newEnemyStates), new
        enemy byllet States (newEnemyBulletsStates) and SpaceShip position after moving (newPos).

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (spaceship.py)
        successorGameState = currentGameState.generateSpaceShipSuccessor(action)
        newPos = successorGameState.getSpaceShipPosition()
        newAsteroid = successorGameState.getAsteroid()
        newEnemyStates = successorGameState.getEnemyStates()
        newEnemyBulletsStates = successorGameState.getEnemyBulletsStates()

        "*** YOUR CODE HERE ***"
        return successorGameState.getScore()


def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the game's GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers. Any methods defined here will be available
    to the MinimaxSpaceShipAgent, AlphaBetaSpaceShipAgent & ExpectimaxSpaceShipAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents. Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated. It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # SpaceShip is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState, agentIndex=0):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means SpaceShip, enemies and bullets are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumMinMaxAgents():
        Returns the total number of agents in the game except the bullets

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState: GameState, agentIndex=0):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState, agentIndex=0):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All enemies should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()


def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme enemy-hunting, asteroid-destroying, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction