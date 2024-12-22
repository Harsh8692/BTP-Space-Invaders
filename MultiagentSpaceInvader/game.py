import pygame
from util import *
import copy

clock = pygame.time.Clock()
pygame.init()

class Directions:
    LEFT = "Left"
    RIGHT = "Right"
    FIRE = "Fire"
    UP = "Up"
    DOWN = "Down"
    STOP = "Stop"

    DCT = {LEFT: LEFT,
           RIGHT: RIGHT,
           FIRE: FIRE,
           UP: UP,
           DOWN: DOWN,
           STOP: STOP}



class Agent:
    """
    Generic agent class that serves as a base for non-static objects in the game,
    such as Spaceship, Enemies, and Bullets.

    An agent must define getAction method.
    Some other methods that can be defined and will be called if they exist:
    def registerInitialState(self, state): # inspects the starting state
    """

    def __init__(self, index = 0):
        self.index = index


    def getAction(self, state):
        """
        The Agent will receive a GameState (from spaceship.py) and 
        must return an action from Directions.{Left, Right, Fire, Up, Down, Stop}
        """
        raiseNotDefined()


class Configuration:
    """
    A configuration holds the (x, y) coordinate of a character.

    The convention for positions, like a graph, is that (0, 0) is the upper left corner, x increases
    horizontally(right) and y increases vertically(down). Therefore, up is the direction of decreasing y.
    """

    def __init__(self, pos): #, directions
        self.pos = pos
        # self.direction = direction

    def getPosition(self):
        return self.pos
    
    # def getDirection(self):
    #     return self.direction
    
    def generateSuccessor(self, delta):
        """
        Generates a new configuration reached by translating the current configuration by the
        action delta. This is a low-level call and does not attempt to respect the legality
        of the movement.
        """
        x, y = self.pos
        ((dx, dy), fire) = delta

        # direction = Actions.vectorToAction(delta)
        return Configuration((x+dx, y+dy)) #, direction


class AgentState:
    """
    AgentStates hold the state of an agent (configuration, isSpaceShip, isUpBullet, isDownBullet, etc).
    """
    def __init__(self, startConfiguration, isSpaceShip, isUpBullet, isDownBullet): 
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.isSpaceShip = isSpaceShip
        self.isUpBullet = isUpBullet
        self.isDownBullet = isDownBullet

    def getPosition(self):
        return self.configuration.getPosition()
    

    def copy(self):
        state = AgentState(self.start, self.isSpaceShip, self.isUpBullet, self.isDownBullet)
        state.configuration = self.configuration
        
        return state


class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.  Data is accessed
    via grid[x][y] where (x,y) are positions on a SpaceShip map with x horizontal,
    y vertical and the origin (0,0) in the upper left corner.

    The __str__ method constructs an output that is oriented like a spaceship board.
    """
    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]: raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other == None: return False
        return self.data == other.data

    def __hash__(self):
        base = 1
        h = 0
        for l in self.data:
            for i in l:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item =True ):
        return sum([x.count(item) for x in self.data])

    def asList(self, key = True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key: list.append( (x,y) )
        return list

    def packBits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index):
        x = index // self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height: break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed, size):
        bools = []
        if packed < 0: raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools

def reconstituteGrid(bitRep):
    if type(bitRep) is not type((1,2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation= bitRep[2:])


####################################
# Parts you shouldn't have to read #
####################################


class Actions:

    """
    A collection of static methods for manipulating move actions.
    """

    _actions = {
        Directions.LEFT : ((-1, 0), 0),
        Directions.RIGHT : ((1, 0), 0),
        Directions.FIRE : ((0, 0), 1), # last 1 specifies fire bullet
        Directions.STOP : ((0, 0), 0),
        # Up and Down are for bullets and enemies only
        Directions.UP : ((0, -1), 0), 
        Directions.DOWN : ((0, 1), 0)
    }

    _actionsAsList = _actions.items()

    def reverseAction(action):
        if (action == Directions.LEFT):
            return Directions.RIGHT
        elif(action == Directions.RIGHT):
            return Directions.LEFT
        elif(action == Directions.UP):
            return Directions.DOWN
        elif(action == Directions.DOWN):
            return Directions.UP
        return action
    reverseAction = staticmethod(reverseAction)

    def vectorToAction(vector):
        ((dx, dy), fire) = vector
        if(dx > 0): return Directions.RIGHT
        if(dx < 0): return Directions.LEFT
        if(dy < 0): return Directions.UP
        if(dy > 0): return Directions.DOWN
        if(dx == 0 and dy == 0):
            if(fire==1): return Directions.FIRE
        return Directions.STOP
    
    vectorToAction = staticmethod(vectorToAction)
    
    def actionToVector(action, speed = 1.0):
        dx, dy = Actions._actions[action][0]
        return ((dx*speed, dy*speed), Actions._actions[action][1])
    
    actionToVector = staticmethod(actionToVector)

    def getPossibleActions(gameState, agentIndex, walls): 
        agentState = gameState.getAgentState(agentIndex)
        width = gameState.data.layout.width
        height = gameState.data.layout.height
        possible = []
        actions = []
        if(agentState.isSpaceShip):
            actions = [Directions.LEFT, Directions.RIGHT, Directions.FIRE, Directions.STOP]
        elif (agentState.isUpBullet):
            actions = [Directions.UP, Directions.STOP]
        elif (agentState.isDownBullet):
            actions = [Directions.DOWN, Directions.STOP]
        else: # enemy
            actions = [Directions.LEFT, Directions.RIGHT, Directions.FIRE, Directions.STOP, Directions.UP, Directions.DOWN]
        x, y = agentState.configuration.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        for act in actions:
            dx, dy = Actions._actions[act][0]
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]: possible.append(act) 

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getSuccessors(position, action, speed=1.0):
        dx, dy = Actions.actionToVector(action, speed)
        x, y = position

        return (x+dx, y+dy)
    
    getSuccessors = staticmethod(getSuccessors)



class GameStateData:
    
    def __init__(self, prevState = None):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.asteroid = prevState.asteroid.shallowCopy()
            self.walls = prevState.walls.shallowCopy()
            self.enemies = prevState.enemies.copy()

            self.agentStates = self.copyAgentStates( prevState.agentStates )
            self.layout = prevState.layout
            self._killed = prevState._killed
            self.score = prevState.score
            

        self._asteroidEaten = None
        self._asteroidAdded = None

        self._killedEnemy = None
        self._agentMoved = None
        self._agentDeleted = []
        self._agentsAdded = []
        self._lose = False
        self._win = False
        self.scoreChange = 0
        
    def deepCopy(self):
        state = GameStateData( self )

        
        state.asteroid = self.asteroid.deepCopy()
        state._asteroidEaten = self._asteroidEaten
        state._asteroidAdded = self._asteroidAdded

        
        state.enemies = copy.deepcopy(self.enemies)
        state.layout = copy.deepcopy(self.layout)
        state._agentMoved = self._agentMoved
        state._killedEnemy = self._killedEnemy
        return state
    
    def copyAgentStates(self, agentStates):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates
    
    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        if other == None: return False
        
        if not self.agentStates == other.agentStates: return False
        if not self.asteroid == other.asteroid: return False
        if not self.score == other.score: return False
        return True

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate( self.agentStates ):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
        return int((hash(tuple(self.agentStates)) + 13*hash(self.asteroid) + 7 * hash(self.score)) % 1048575 )

    def __str__( self ):
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if type(self.asteroid) == type((1,2)):
            self.asteroid = reconstituteGrid(self.asteroid)
        for x in range(width):
            for y in range(height):
                asteroid, walls = self.asteroid, self.layout.walls
                map[x][y] = self._asteroidWallStr(asteroid[x][y], walls[x][y]) 


        for agentState in self.agentStates:
            if agentState == None: continue
            if agentState.configuration == None: continue
            x,y = [int( i ) for i in nearestPoint( agentState.configuration.pos )]
            if agentState.isSpaceShip:
                map[x][y] = 'S'
            elif agentState.isUpBullet:
                map[x][y] = '^'
            elif agentState.isDownBullet:
                map[x][y] = 'v'
            else:
                map[x][y] = 'E'


        return str(map) + ("\nScore: %d\n" % self.score)
    
    def _asteroidWallStr( self, hasAsteroid, hasWall ): 
        if hasAsteroid:
            return 'o'
        elif hasWall: 
            return '%'
        else : #for empty space
            return ' ' 


    def initialize(self, layout, numEnemyAgents):
        """
        Creates an initial game state from a layout array (see layout.py).
        """

        self.asteroid = layout.asteroid.copy()
        self.walls = layout.walls.copy()

        self.enemies = layout.getEnemies()
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentStates = []
        numEnemies = 0

        for isSpaceShip, isUpBullet, isDownBullet, pos in layout.agentPositions:
            if not isSpaceShip:
                if numEnemies == numEnemyAgents: continue
                else: numEnemies += 1
            self.agentStates.append( AgentState( Configuration(pos), isSpaceShip, isUpBullet, isDownBullet))
        
        self._killed = [False for a in self.agentStates]


class Game:
    """
    The game manages the control flow, soliciting actions from the agents.
    """

    def __init__(self, agents, display, rules, startingIndex = 0, muteAgents=False, catchExceptions=False, numEnemiesBullets=1):
        self.agents = agents
        self.maxNumEnemiesBullets = numEnemiesBullets
        self.display = display
        self.rules = rules
        self.startingIndex =startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io
        self.agentOutput = [io.StringIO() for agent in agents]

    
        
    def run(self):
        """
        Main control loop for game play.
        """

        self.display.initialize(self.state.data)
        self.numMoves = 0

        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]

            if ("registerInitialState" in dir(agent)):
                agent.registerInitialState(self.state.deepCopy())

        agentIndex = self.startingIndex
        numAgents = len( self.agents )

        while not self.gameOver:

            # when to exit game volunteerily
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Space Invader exited! Score: %d" % self.state.data.score)
                    self.gameOver = True
            
            # Fetch the next agent
            agent = self.agents[agentIndex]
            # Generate an observation of the state
            observation = self.state.deepCopy() 

            # Solicit an action
            action = agent.getAction(observation, agentIndex) 

            # Execute the action
            self.moveHistory.append((agentIndex, action))
            newState = self.state.generateSuccessor( agentIndex, action ) 

            for agent in newState.data._agentsAdded: 
                self.agents.append(agent)
            for idx in sorted(newState.data._agentDeleted, reverse=True): 
                del self.agents[idx]
                del newState.data.agentStates[idx]
            
            agentIndex = newState.data._agentMoved #this _agentMoved specifies the last moved agent among the current agents
            # since some of the agents might have been removed while generating successors
        
            numAgents = len(self.agents) 
            agentIndex %= numAgents
            

            self.state = newState
            # self.state.data._agentMoved = agentIndex

            # Change the display
            self.display.update( self.state.data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(newState, self)

            # Next agent
            agentIndex = ( agentIndex + 1) % numAgents

            clock.tick(60)

        