"""
Spaceship.py holds the logic for the classic space invader game with some changes (like adding asteroids)
along with the main code to run a game. This file is divided into three sections:

    (i)     Your interface to the space invader world:
                Space Invader is a complex environment. You probably don't want to
                read through all of the code we wrote to make the game runs
                correctly. This section contains the parts of the code
                that you will need to understand in order to complete the
                project. There is also some code in game.py that you should
                understand.
    
    (ii)    The hidden secrets of space invader:
                This section contains all of the logic code that the space invader
                environment uses to decide who can move where, who dies when
                bullets hit, etc. You shouldn't need to read this section
                of code, but you can if you want.

    (iii)   Framework to start a game:
                The final section contains the code for reading the command
                you use to set up the game, then starting up a new game, along with
                linking in all the external parts (agent functions, graphics).
                Check this section out to see all the options available to you.

To play your first game, type 'python spaceship.py' from the command line.
The keys are backspace(to fire), left arrow and right arrow to move. Have fun :).
"""

# import random
import pygame
from pygame import mixer
import sys
from game import GameStateData
from game import Game
from game import Actions
import graphicsDisplay
import layout
from keyboardAgents import KeyboardAgent
from enemyAgents import  RandomAgent
from bulletAgents import *
from game import AgentState, Configuration
from util import *
from game import Directions
import os


##########################################################
# YOUR INTERFACE TO THE SPACE INVADER WORLD: A GameState #
##########################################################


TIME_PENALTY = 1


class GameState:
    """
    A GameState specifies the full game state, including agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note: Spaceship is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    explored = set() # static variable to keep track of which states have had getLegalActions called
    def getAndResetExplored():
        temp = GameState.explored.copy()
        GameState.explored = set()
        return temp
    getAndResetExplored = staticmethod(getAndResetExplored)

    def getLegalActions(self, agentIndex = 0):
        """
        Return the legal actions for the agent specified.
        """
        if self.isWin() or self.isLose(): return []

        if agentIndex >= len(self.data.agentStates):
            return []

        if agentIndex == 0:
            return SpaceShipRules.getLegalActions(self)
        elif self.data.agentStates[agentIndex].isUpBullet or self.data.agentStates[agentIndex].isDownBullet: 
            return BulletRules.getLegalActions(self, agentIndex)
        else:
            return EnemyRules.getLegalActions(self, agentIndex)

    def generateSuccessor(self, agentIndex, action): 
        """
        Returns the successor state after the specified agent takes the action.
        """
        #checking if the successor exist
        if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')
        #copy of current state
        state = GameState(self)
        
        if(agentIndex>=len(state.data.agentStates) and not state.data._win): # This is just for testing purpose
            print("Warning: The game stopped due to index going out of bound need to tackle it.")
            state.data._lose = True
            return state

        state.data._agentMoved = agentIndex # _agentMoved might get changed according to further function calls
        agentDestroyed = False
        if agentIndex == 0: # it is spaceship
            SpaceShipRules.applyAction( state, action) 
        
        elif state.data.agentStates[agentIndex].isUpBullet or state.data.agentStates[agentIndex].isDownBullet:
            agentDestroyed = BulletRules.applyAction(state, action, agentIndex) 
        else: 
            EnemyRules.applyAction( state, action, agentIndex) 

        # as time passes
        if agentIndex == 0:
            state.data.scoreChange += -TIME_PENALTY # penalty for waiting around

        # death through bullets check
        if not agentDestroyed: BulletRules.checkDeath(state, agentIndex)

        #book keeping
        state.data._agentDeleted = list(set(state.data._agentDeleted))
        state.data.score += state.data.scoreChange
        GameState.explored.add(self)
        GameState.explored.add(state) # state has been updated due to action 

        return state


    def getSingleAsteroidLocation(self):

        for xNum, x in enumerate(self.data.asteroid):
            for yNum, cell in enumerate(x):
                if cell:
                    return (xNum, yNum)


    def getLegalSpaceShipAction( self ):
        return self.getLegalActions( 0 )
    
    def generateSpaceShipSuccessor(self, action):
        """
        Generates the successor state after the specified spaceship move
        """
        return self.generateSuccessor( 0, action)
    
    def getSpaceShipState(self):
        """
        returns an AgentState object for SpaceShip
        """

        return self.data.agentStates[0].copy()
    
    def getSpaceShipPosition( self ):
        return self.data.agentStates[0].getPosition()
    
    
    def getEnemyStates( self ):
        return [state for state in self.data.agentStates if not state.isSpaceShip and not state.isUpBullet and not state.isDownBullet]

    def getEnemyBulletsStates( self ):
        return [state for state in self.data.agentStates if state.isDownBullet]
    
    def getSpaceShipBulletsStates(self):
        return [state for state in self.data.agentStates if state.isUpBullet]
    
    
    def getAgentState(self, agentIndex):
        return self.data.agentStates[agentIndex]
    
    def getEnemyState( self, agentIndex ):
        if agentIndex == 0 or agentIndex > self.getNumEnemies():
            raise Exception("Invalid index passed to getEnemyState")
        return self.data.agentStates[agentIndex]
    
    def getEnemyPosition( self, agentIndex ):
        if agentIndex == 0:
            raise Exception("SpaceShip's index passed to getEnemyPosition")
        return self.data.agentStates[agentIndex].getPosition()
    
    def getEnemyPositions( self ):
        return [s.getPosition() for s in self.getEnemyStates()]
    
    def getBulletStates(self):
        return [state for state in self.data.agentStates  if state.isUpBullet or state.isDownBullet]
    
    def getBulletPositions(self):
        return [s.getPosition() for s in self.getBulletStates()]
    
    def getNumAgents( self ):
        return len(self.data.agentStates)
    
    def getNumEnemies(self):
        return len(self.getEnemyStates())
    
    def getNumEnemyBullets(self):
        return len(self.getEnemyBulletsStates())
    
    def getNumBullets(self):
        return len(self.getBulletStates())

    
    def getMinMaxAgents(self):
        return [idx for idx, state in enumerate(self.data.agentStates) if (not state.isUpBullet and not state.isDownBullet)]
    
    def getBulletAgents(self):
        return [idx for idx, state in enumerate(self.data.agentStates) if (state.isUpBullet or state.isDownBullet)]
    
    def getNumMinMaxAgents(self):
        return len(self.getMinMaxAgents())

    def getScore( self ):
        return float(self.data.score)

    def getNumAsteroid( self ):
        return self.data.asteroid.count()
    
    def getAsteroid(self):
        """
        Returns a Grid of boolean asteroid indicator variables.

        Grids can be accessed via list notation, so to check
        if there is asteroid at (x,y), just call

        currentAsteroid = state.getAsteroid()
        if currentAsteroid[x][y] == True: ...
        """
        return self.data.asteroid
    
    def getWalls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    
    def hasAsteroid(self, x, y):
        return self.data.asteroid[x][y]
    
    def hasWall(self, x, y):
        return self.data.layout.walls[x][y]
    
    def isLose( self ):
        return self.data._lose

    def isWin( self ):
        return self.data._win
    
    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__( self, prevState = None ):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None:
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy( self ):
        state = GameState(self)
        state.data = self.data.deepCopy()
        return state

    def __eq__( self, other ):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__( self ):
        """
        Allows states to be keys of dictionaries.
        """
        return hash( self.data )

    def __str__( self ):

        return str(self.data)
    
    def initialize( self, layout, numEnemyAgents):
        """
        Creates an initial game state from the layout array (see layout.py).
        """
        self.data.initialize(layout, numEnemyAgents)


class ClassicGameRules:
    """
    These game rules manage the control flow of a game, deciding when and how the game starts and ends.
    """

    def __init__(self):
        pass

    def newGame( self, layout, sapceShipAgent, enemyAgents, display, quiet = False, catchExceptions = False):
        agents = [sapceShipAgent] + enemyAgents[:layout.getNumEnemies()]
        initState = GameState()
        initState.initialize( layout, len(enemyAgents) )
        game = Game(agents, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game
    
    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """

        if state.isWin(): self.win(state, game)
        if state.isLose(): self.lose(state, game)

    def win(self, state, game):

        if not self.quiet: print("SpaceShip wins! Score: %d" % state.data.score)
        game.gameOver = True

    def lose(self, state, game):

        if not self.quiet: print("SpaceShip destroyed! Score: %d" % state.data.score)
        game.gameOver = True

    def getProgress(self, game):
        return float(game.state.getNumEnemies()) / self.initialState.getNumEnemies()
    

class SpaceShipRules:
    """
    There functions govern how spaceship interacts with his environment under 
    the classic game rules.
    """
    SPACESHIP_SPEED = 1.0

    def getLegalActions( state ):
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions(state, 0, state.data.layout.walls)
        
    getLegalActions = staticmethod(getLegalActions)

    def applyAction(state, action): 
        """
        Edits the state to reflect the results of the action.
        """
        legal = SpaceShipRules.getLegalActions( state )
        if action not in legal:
            raise Exception("Illegal action " + str(action))
        
        # here state is gamestate 
        spaceShipState = state.data.agentStates[0]

        if action in [Directions.LEFT, Directions.RIGHT, Directions.STOP]:
            vector = Actions.actionToVector(action,SpaceShipRules.SPACESHIP_SPEED)
            spaceShipState.configuration = spaceShipState.configuration.generateSuccessor(vector)
        elif action == Directions.FIRE:
            SpaceShipRules.fire(state) 

    
    applyAction = staticmethod(applyAction)

    def fire(state): 
        """
        Creates a new Bullet agent and agentState when the spaceship fires.
        """
        spaceshipPosition = state.getSpaceShipPosition()
        x, y = spaceshipPosition
        bullet = AgentState(Configuration((x, y-1)), False, True, False) #, Directions.STOP
        state.data._agentsAdded.append(UpBulletAgent(len(state.data.agentStates))) 
        state.data.agentStates.append(bullet)

    fire = staticmethod(fire)


class EnemyRules:
    """
    These functions dictate how enemies interact with their environment.
    """
    ENEMY_SPEED = 1.0
    def getLegalActions( state, enemyIndex):
        """
        Returns legal actions for an enemy with enemyIndex.
        """
        enemyState = state.getEnemyState( enemyIndex )
        possibleActions = Actions.getPossibleActions(state, enemyIndex, state.data.layout.walls) 
        return possibleActions
    
    getLegalActions = staticmethod(getLegalActions)

    def applyAction( state, action, enemyIndex ): 
        legal = EnemyRules.getLegalActions(state, enemyIndex)
        if action not in legal:
            raise Exception("Illegal Enemy action " + str(action))
        
        enemyState = state.data.agentStates[enemyIndex]
        speed = EnemyRules.ENEMY_SPEED

        if action in [Directions.UP, Directions.DOWN, Directions.LEFT, Directions.RIGHT, Directions.STOP]:
            vector = Actions.actionToVector(action, speed)
            enemyState.configuration = enemyState.configuration.generateSuccessor( vector )
        elif action == Directions.FIRE:
            EnemyRules.fire(state, enemyIndex) 

    applyAction = staticmethod(applyAction)


    def fire(state, enemyIndex): 
        enemyPosition = state.getEnemyPosition(enemyIndex)
        x, y = enemyPosition
        bullet = AgentState(Configuration((x, y+1)), False, False, True)
        state.data._agentsAdded.append(DownBulletAgent(len(state.data.agentStates))) 
        state.data.agentStates.append(bullet) 

    fire = staticmethod(fire)


    def placeEnemy(state, enemyState):
        enemyState.configuration = enemyState.start

    placeEnemy = staticmethod(placeEnemy)



class BulletRules:
    """
    These functions govern how bullets interact with their environment.
    """
    BULLET_SPEED = 1

    def getLegalActions(state, bulletIndex):
        """
        Spaceship's(Up) bullets moves upward.
        Enemy's(Down) bullets moves downward.
        """
        if state.data.agentStates[bulletIndex].isUpBullet:
            return [Directions.UP]
        else: return [Directions.DOWN]

    getLegalActions = staticmethod(getLegalActions)
    
    def applyAction(state, action, bulletIndex): 

        bulletState = state.data.agentStates[bulletIndex]
        speed = BulletRules.BULLET_SPEED
        # Update configuration
        vector = Actions.actionToVector(action, speed)
        bulletState.configuration = bulletState.configuration.generateSuccessor(vector)

        next = bulletState.configuration.getPosition()
        nearest = nearestPoint( next )
        # Remove bullet if it goes off-screen
        state.data._agentMoved = bulletIndex
        x, y = nearest
        x = min(int(x), state.data.walls.width-1)
        y = min(int(y), state.data.walls.height-1)
        if state.data.walls[x][y]:

            state.data._agentDeleted.append(bulletIndex)
            state.data._agentMoved = bulletIndex - 1 #since the current index is destroyed 
            return True
        # Eat asteroid only when bullet is fired from the spaceship not the enemy
        if state.data.agentStates[bulletIndex].isUpBullet :#and manhattanDistance( nearest, next ) <= 0.5
            # Remove asteroid
            return BulletRules.consume( nearest, state, bulletIndex ) 
            
        return False


    applyAction = staticmethod(applyAction)


    def consume( position, state, bulletIndex ): 
        x, y = position
        # Eat asteroid
        state.data._agentMoved = bulletIndex

        if state.data.asteroid[x][y]:
            state.data.scoreChange += 100
            state.data.asteroid = state.data.asteroid.copy()
            state.data.asteroid[x][y] = False
            state.data._asteroidEaten = position


            state.data._agentMoved = bulletIndex - 1 #since the current index is destroyed 
            state.data._agentDeleted.append(bulletIndex)
            
            numAsteroid = state.getNumAsteroid()
            if numAsteroid == 0 and not state.data._lose : #and not state.data._win
                state.data.scoreChange += 500
                state.data._win = True
            return True
        
        return False
    
    consume = staticmethod(consume)


    def checkDeath(state, agentIndex):
        agentState = state.data.agentStates[agentIndex]
        state.data._agentMoved = agentIndex
        if agentState.isSpaceShip: # spaceship just moved so down bullets can kill it
            spaceshipPosition = agentState.configuration.getPosition()
            for index in range(len(state.data.agentStates)):
                ast = state.data.agentStates[index]
                aPos = ast.configuration.getPosition()
                if ast.isDownBullet:
                    if BulletRules.canHit(spaceshipPosition, aPos):
                        state.data._agentMoved -= 2 #spaceship and bullet destroyed
                        if not state.data._win:
                            state.data.scoreChange -= 500
                            state.data._lose = True

        elif agentState.isUpBullet: # bullet moved so can kill enemy or down bullet
            upbulletPosition = agentState.configuration.getPosition()
            for index in range(len(state.data.agentStates)):
                bst = state.data.agentStates[index]
                bPos = bst.configuration.getPosition()
                if bst.isDownBullet:
                    if BulletRules.canHit(upbulletPosition, bPos):
                        state.data._agentMoved -= 1 #since current bullet is destroyed
                        if index < agentIndex:
                            state.data._agentMoved -= 1
                        state.data._agentDeleted.append(agentIndex)
                        state.data._agentDeleted.append(index)

                elif not bst.isSpaceShip and not bst.isUpBullet and not bst.isDownBullet: #enemy
                    if BulletRules.canHit(upbulletPosition, bPos):
                        # need to placeEnemy or respawn it
                        EnemyRules.placeEnemy(state, state.data.agentStates[index])
                        state.data._killed[index] = True
                        state.data._agentMoved -= 1
                        state.data._agentDeleted.append(agentIndex)
                        state.data.scoreChange += 100

        elif agentState.isDownBullet: #bullet moved so can kill spaceship or up bullet
            downbulletPosition = agentState.configuration.getPosition()
            for index in range(len(state.data.agentStates)):
                bst = state.data.agentStates[index]
                bPos = bst.configuration.getPosition()
                if bst.isUpBullet:
                    if BulletRules.canHit(downbulletPosition, bPos):
                        #adding bullets to be destroyed
                        state.data._agentMoved -= 1 #since current bullet is destroyed
                        if index < agentIndex:
                            state.data._agentMoved -= 1
                        state.data._agentDeleted.append(agentIndex)
                        state.data._agentDeleted.append(index)
                elif bst.isSpaceShip:
                    if BulletRules.canHit(downbulletPosition, bPos):
                        #need to reomve bullets and spaceship
                        state.data._agentDeleted.append(agentIndex)
                        state.data._agentDeleted.append(index)
                        state.data._agentMoved -= 2
                        if not state.data._win : #and not state.data._lose
                            state.data.scoreChange -= 500
                            state.data._lose = True
                        
                    
        else:
            enemyPosition = agentState.configuration.getPosition()
            for index in range(len(state.data.agentStates)):
                bst = state.data.agentStates[index]
                bPos = bst.configuration.getPosition()
                if bst.isUpBullet:
                    if BulletRules.canHit(enemyPosition, bPos):
                        #need to respawn the enemy
                        EnemyRules.placeEnemy(state, state.data.agentStates[agentIndex])
                        state.data._killed[agentIndex] = True
                        state.data._agentMoved -= 1
                        state.data._agentDeleted.append(index)
                        state.data.scoreChange += 100
            
            


    def canHit(aPos, bPos):
        return manhattanDistance(aPos, bPos) <= 0.75

    canHit = staticmethod(canHit)

    


###################################
#   FRAMEWORK TO START THE GAME   #
###################################


def default(str):
    return str + ' [Default: %default]'

def getLayout(filename):
    file_path = 'layouts/' + filename + '.lay'
    
    return file_path

def parseAgentArgs(str):
    if str == None: return {}
    pieces = str.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key,val = p, 1
        opts[key] = val
    return opts


def readCommand( argv ):
    """
    Processes the command used to run space invaders from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python spaceship.py <options>
    EXAMPLES:   (1) python spaceship.py
                    - starts an interactive game
                (2) python spaceship.py --layout layout1
                OR  python spaceship.py -l layout1
                    - starts an interactive game on layout1 board
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='general')
    parser.add_option('-s', '--spaceship', dest='spaceship',
                      help=default('the agent TYPE in the spaceshipAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-e', '--enemy', dest='enemy',
                      help=default('the agent TYPE in the enemyAgents module to use'),
                      metavar='TYPE', default='RandomAgent')
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-a','--agentArgs',dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()


    # Choose a layout
    args['layout'] = layout.getLayout(options.layout)
    if args['layout'] == None: raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a Spaceship agent
    noKeyboard = options.textGraphics or options.quietGraphics
    spaceshipType = loadAgent(options.spaceship, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    
    spaceship = spaceshipType(**agentOpts)
    args['spaceship'] = spaceship

    # Choose an enemy agent
    enemyType = loadAgent(options.enemy, noKeyboard)
    args['enemy'] = [enemyType(i+1) for i in range(args['layout'].getNumEnemies())]


    # # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        args['display'] = textDisplay.SpaceShipGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.SpaceShipGraphics(options.zoom) # need to check the frame time thing once.


    args['numGames'] = options.numGames

    return args

def loadAgent(spaceship, nographics):
    # Looks through all pythonPath Directories for the right module,
    pythonPathStr = os.path.expandvars("$PYTHONPATH")
    if pythonPathStr.find(';') == -1:
        pythonPathDirs = pythonPathStr.split(':')
    else:
        pythonPathDirs = pythonPathStr.split(';')
    pythonPathDirs.append('.')

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir): continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError as e:
                # Print the error for better debugging
                print(f"ImportError while importing {modulename}: {e}")
                continue

            if spaceship in dir(module):
                if nographics and modulename == 'keyboardAgents.py':
                    raise Exception('Using the keyboard requires graphics (not text display)')
                return getattr(module, spaceship)
    raise Exception('The agent ' + spaceship + ' is not specified in any *Agents.py.')


def run_games(spaceship, numGames, enemy, layout, display):
    
    rules = ClassicGameRules()
    games = []

    for i in range( numGames ):

        gameDisplay = display

        game = rules.newGame(layout, spaceship, enemy, gameDisplay)
        game.run()
        games.append(game)

    scores = [game.state.getScore() for game in games]
    wins = [game.state.isWin() for game in games]
    winRate = wins.count(True)/ float(len(wins))
    print('Average Score:', sum(scores)/ float(len(scores)))
    print('Scores:       ', ', '.join([str(score) for score in scores]))
    print('Win Rate:      %d/%d (%.2f)' % (wins.count(True), len(wins), winRate))
    print('Record:       ', ', '.join([ ['Loss', 'Win'][int(w)] for w in wins]))

    return games


if __name__ == '__main__':
    """
    The main function called when spaceship.py is run 
    from the command line:

    > python spaceship.py

    See the usage string for more details.

    > python spaceship.py --help
    """

    args = readCommand(sys.argv[1:])
    run_games(**args)

    pass