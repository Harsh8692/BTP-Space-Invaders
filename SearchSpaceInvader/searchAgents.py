"""
This file contains all of the agents that can be selected to control SpaceShip. To select
an agent, use the '-s' option when running spaceship.py. Arguments can be passed to your
agent using '-a'. For example to load, a SearchAgent that uses depth first search (dfs),
run the following command:

> python spaceship.py -s SearchAgent -a fn=depthFirstSearch

Commands to invoke other search strategies can be found in the project
description.

Please only change the parts of the file you are asked to. Look for the lines
that say

"*** YOUR CODE HERE ***"

Good luck and happy searching!
"""

from game import Directions
from game import Agent
from game import Actions
import util
import time
import search
import spaceship


#######################################################
# This portion is written for you, but will only work #
#       after you fill in parts of search.py          #
#######################################################

class SearchAgent(Agent):
    """
    This very general search agent finds a path using a supplied search
    algorithm for a supplied search problem, then returns actions to follow that
    path.

    As a default, this agent runs DFS on a PositionSearchProblem to find
    location of a single asteroid present in the layout. If there are 
    multiple asteroids it only searches for the first asteroid according 
    to the grid.

    Options for fn include:
      depthFirstSearch or dfs
      breadthFirstSearch or bfs


    Note: You should NOT change any code in SearchAgent
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems

        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic + ' is not a function in searchAgents.py or search.py.')
            print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in searchAgents.py.')
        self.searchType = globals()[prob]
        print('[SearchAgent] using problem type ' + prob)

    def registerInitialState(self, state):
        """
        This is the first time that the agent sees the layout of the game
        board. Here, we choose a path to the goal. In this phase, the agent
        should compute the path to the goal and store it in a local variable.
        All of the work is done in this method!

        state: a GameState object (spaceship.py)
        """
        if self.searchFunction == None: raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path

        if self.actions == None:
            self.actions = []
        totalCost = problem.getCostOfActions(self.actions)
        print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

    def getAction(self, state, agentIndex):
        """
        Returns the next action in the path chosen earlier (in
        registerInitialState).  Return Directions.STOP if there is no further
        action to take.

        state: a GameState object (spaceship.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    A search problem defines the state space, start state, goal test, successor
    function and cost function. This search problem can be used to find paths
    to a particular point on the Space Invaders board.

    The state space consists of (x,y) positions in a Space Invaders game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        Stores the start and goal.

        gameState: A GameState object (spaceship.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls() 
        self.startState = (gameState.getSpaceShipPosition(), ()) # () specifies the bullets fired
        if start != None: self.startState = start
        x, y = gameState.getSpaceShipPosition()
        self.singleAsteroidLocation =  gameState.getSingleAsteroidLocation()
        if(goal != self.singleAsteroidLocation):
            goal = self.singleAsteroidLocation
        gx, gy = goal
        self.goal = ((gx, y), (gx, y)) # need to check the enumeration # we are searching for asteroid at (1, 1) so we fire at (1, y)
        self.costFn = costFn
        self.visualize = visualize
        
        if warn and (gameState.getNumAsteroid() != 1 ):  # goal[1] specify the no of asteroids in the goal state.
            print('Warning: this does not look like a regular search maze')

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        
        for action in [Directions.LEFT, Directions.RIGHT, Directions.FIRE, Directions.STOP]:
            
            x, y = state[0]

            ((dx, dy), fire) = Actions.actionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)

            if self.walls[nextx][nexty]: 
                continue 

            if (fire):
                newState = ((nextx, nexty), (nextx, nexty))
                cost = self.costFn(newState)
                successors.append((newState, action, cost))
            
            else:
                newState = ((nextx, nexty), state[1])
                cost = self.costFn(newState)
                successors.append((newState, action, cost))
        

        # Bookkeeping 
        self._expanded += 1 # DO NOT CHANGE
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        """
        
        if actions == None: return 999999
        
        state = self.getStartState()
        x,y= state[0]
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.actionToVector(action)[0]
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999 
            cost += self.costFn(((x,y), state[1]))
        return cost


class StayRightSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being 
    in positions on the Left side of the board.

    The cost function for stepping into a position (x, y) is 1/2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        
        costFn = lambda pos: (0.5 ** pos[0][0])
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (23, 1), None, False)


class StayLeftSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being 
    in positions on the Right side of the board.

    The cost function for stepping into a position (x, y) is 2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        
        costFn = lambda pos: (2 ** (pos[0][0]))
        self.searchType = lambda state: PositionSearchProblem(state, costFn, (1, 1), None, False)

def semimanhattanHeuristic(position, problem, info={}):
    "This is semi manhattan Heuristic only for horizontal direction"
    xy1 = position[0]
    xy2 = problem.goal[0]
    return abs(xy1[0]-xy2[0])



#####################################################
# This portion is incomplete. Time to write code!   #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    This search problem finds paths for the spaceship to shoot the top left and top right corners of a layout.

    You must select a suitable state space and successor function
    """

    def __init__(self, startingGameState: spaceship.GameState):
        """
        Stores the walls, spaceship's starting position, top left and top right corners.
        """
        self.walls = startingGameState.getWalls() 
        self.layout = startingGameState.data.layout
        self.startingPosition = startingGameState.getSpaceShipPosition()
        
        top, right = self.walls.height-2, self.walls.width-2 
        self.corners = ((1, 1), (right, 1))
        
        for corner in self.corners:
            if not startingGameState.hasAsteroid(*corner):
                print('Warning: no asteroid in corner ' + str(corner))
        self._expanded = 0 # DO NOT CHANGE; Number of search nodes expanded

        # Please add any code here which you would like to use in initializing the problem
        "*** YOUR CODE HERE ***"

    def getStartState(self):
        """
        Returns the start state (in your state space, not the full Spaceship state
        space)
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
        Returns whether this search state is a goal state of the problem.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
            For a given state, this should return a list of triples, (successor,
            action, stepCost), where 'successor' is a successor to the current
            state, 'action' is the action required to get there, and 'stepCost'
            is the incremental cost of expanding to that successor
        """

        successors = []
        for action in [Directions.LEFT, Directions.RIGHT, Directions.FIRE, Directions.STOP]:
            # Add a successor state to the successor list if the action is legal
            # x, y = state[0]
            # ((dx, dy), fire) = Actions.actionToVector(action)
            # nextx, nexty = int(x + dx), int(y + dy)
            # hitsWall = self.walls[nextx][nexty]

            "*** YOUR CODE HERE ***"

        self._expanded += 1 # DO NOT CHANGE
        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.  This is implemented for you.
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.actionToVector(action)[0]
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999 
        return len(actions)


def cornersHeuristic(state, problem: CornersProblem):
    """
    A heuristic for the CornersProblem that you defined.

      state:   The current search state
               (a data structure you chose in your search problem)

      problem: The CornersProblem instance for this layout.

    This function should always return a number that is a lower bound on the
    shortest path from the state to a goal of the problem; i.e.  it should be
    admissible (as well as consistent).
    """
    corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the game frame.

    "*** YOUR CODE HERE ***"
    return 0 # Default to trivial solution


class AStarCornersAgent(SearchAgent):
    "A SearchAgent for AsteroidSearchProblem using A* and your asteroidHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem


class AsteroidSearchProblem:
    """
    A search problem associated with finding the path that shoot down all of the
    Asteroids in a Space Invader game.

    A search state in this problem is a tuple ( spaceshipPosition, asteroidGrid ) where
      spaceshipPosition: a tuple (x,y) of integers specifying Spaceship's position
      asteroidGrid:       a Grid (see game.py) of either True or False, specifying remaining asteroid
    """
    def __init__(self, startingGameState: spaceship.GameState):
        self.start = (startingGameState.getSpaceShipPosition(), startingGameState.getAsteroid())
        self.walls = startingGameState.getWalls() 
        self.startingGameState = startingGameState
        self._expanded = 0 # DO NOT CHANGE
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost of 1."
        successors = []
        self._expanded += 1 # DO NOT CHANGE

        for action in [Directions.LEFT, Directions.RIGHT, Directions.FIRE, Directions.STOP]:
            x, y = state[0]
            ((dx, dy), fire) = Actions.actionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            nextAsteroid = state[1].copy()

            if self.walls[nextx][nexty]: 
                continue 


            if(fire):
                for ht in range(nexty, 0, -1):

                    if(nextAsteroid[nextx][ht]):
                        nextAsteroid[nextx][ht]=False
                        break
                
                successors.append((((nextx, nexty), nextAsteroid), action, 1))
            else:
                successors.append((((nextx, nexty), nextAsteroid), action, 1))

        return successors
                

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.actionToVector(action)[0]
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: 
                return 999999
            cost += 1
        return cost


class AStarAsteroidSearchAgent(SearchAgent):
    "A SearchAgent for AsteroidSearchProblem using A* and your asteroidHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, asteroidHeuristic)
        self.searchType = AsteroidSearchProblem

def asteroidHeuristic(state, problem: AsteroidSearchProblem):
    """
    Your heuristic for the AsteroidSearchProblem goes here.

    This heuristic must be consistent to ensure correctness. First, try to come
    up with an admissible heuristic; almost all admissible heuristics will be
    consistent as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible! On the
    other hand, inadmissible or inconsistent heuristics may find optimal
    solutions, so be careful.

    The state is a tuple ( spaceshipPosition, asteroidGrid ) where asteroidGrid is a Grid
    (see game.py) of either True or False. You can call asteroidGrid.asList() to get
    a list of asteroid coordinates instead.

    If you want access to info like walls, asteroids, etc., you can query the
    problem. For example, problem.walls gives you a Grid of where the walls
    are.

    If you want to *store* information to be reused in other calls to the
    heuristic, there is a dictionary called problem.heuristicInfo that you can
    use. For example, if you only want to count the walls once and store that
    value, try: problem.heuristicInfo['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access
    problem.heuristicInfo['wallCount']
    """
    position, asteroidGrid = state
    "*** YOUR CODE HERE ***"
    return 0


class ClosestDotSearchAgent(SearchAgent):
    "Search for all asteroid using a sequence of searches"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        
        while(currentState.getAsteroid().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()

                if action not in legal:
                    break

                currentState = currentState.generateSuccessor(0, action)

        self.actionIndex = 0
        print('Path found with cost %d.' % len(self.actions))

    def findPathToClosestDot(self, gameState: spaceship.GameState):
        """
        Returns a path (a list of actions) to the closest dot, starting from
        gameState.
        """
        # Here are some useful elements of the startState
        startPosition = gameState.getSpaceShipPosition()
        asteroid = gameState.getAsteroid()
        walls = gameState.getWalls() 
        problem = AnyAsteroidSearchProblem(gameState)

        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

class AnyAsteroidSearchProblem(PositionSearchProblem):
    """
    A search problem for finding a path to any asteroid.

    This search problem is just like the PositionSearchProblem, but has a
    different goal test, which you need to fill in below. The state space and
    successor function do not need to be changed.

    The class definition above, AnyAsteroidSearchProblem(PositionSearchProblem),
    inherits the methods of the PositionSearchProblem.

    You can use this search problem to help you fill in the findPathToClosestDot
    method.
    """

    def __init__(self, gameState):
        "Stores information from the gameState.  You don't need to change this."
        # Store the asteroid for later reference
        self.asteroid = gameState.getAsteroid()
        self.gState = gameState
        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls() #for walls
        self.startState = (gameState.getSpaceShipPosition(), ()) # () specifies the bullets fired
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE


    def isGoalState(self, state):
        """
        The state is tuple of SpaceShip's position and bullets fired postion. Fill this in with a goal test that will
        complete the problem definition.
        """
        
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()



def mazeDistance(point1, point2, gameState: spaceship.GameState) -> int:
    """
    Returns the maze distance between any two points, using the search functions
    you have already built. The gameState can be any game state -- SpaceShip's
    position in that state is ignored.

    Example usage: mazeDistance( (2,4), (5,6), gameState)

    This might be a useful helper function for your ApproximateSearchAgent.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + str(point1) 
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2) 
    prob = PositionSearchProblem(gameState,  goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))