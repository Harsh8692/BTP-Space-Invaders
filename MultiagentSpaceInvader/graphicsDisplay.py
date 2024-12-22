import pygame
import math
import time
from queue import Queue
from util import manhattanDistance

def format_color(r, g, b):
    return (int(r * 255), int(g * 255), int(b * 255))

ENEMY_IMAGE_FILE = "img/enemy.png"
SPACESHIP_IMAGE_FILE = "img/space-invaders.png"
BULLET_IMAGE_FILE = "img/bullet.png"
ASTEROID_IMAGE_FILE = "img/asteroid.png"
WALL_IMAGE_FILE = "img/wall.png"
ICON_IMAGE_FILE = "img/ufo.png"

DEFAULT_GRID_SIZE = 35.0
INFO_PANE_HEIGHT = 35
BACKGROUND_COLOR = format_color(0, 0, 0)
WHITE_COLOR = format_color(1, 1, 1)


pygame.font.init()

class SpaceShipGraphics:
    def __init__(self, zoom=1.0, capture=False):
        pygame.init()
        self.have_window = False
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.capture = capture

        # Load Images
        self.spaceshipImage = self.loadImage(SPACESHIP_IMAGE_FILE)
        self.enemyImage = self.loadImage(ENEMY_IMAGE_FILE)
        self.bulletImage = self.loadImage(BULLET_IMAGE_FILE)
        self.asteroidImage = self.loadImage(ASTEROID_IMAGE_FILE)
        self.wallImage = self.loadImage(WALL_IMAGE_FILE)
        self.iconImage = self.loadImage(ICON_IMAGE_FILE)
        self.rotatedBulletImage = pygame.transform.rotate(self.bulletImage, 180)
        self.keys_pressed = set()

    def loadImage(self, filename, factor=1.0):
        image = pygame.image.load(filename)
        return pygame.transform.scale(image, (int(self.gridSize/factor), int(self.gridSize/factor)))

    def initialize(self, state):
        self.startGraphics(state)

        self.drawStaticObjects(state)

        self.drawAgentObjects(state)
        self.previousState = state

    def startGraphics(self, state):
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.screen_width = (self.width ) * self.gridSize 
        self.screen_height = (self.height ) * self.gridSize + INFO_PANE_HEIGHT 
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Space Invaders')
        pygame.display.set_icon(self.iconImage)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(BACKGROUND_COLOR)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.have_window = True

    def drawStaticObjects(self, state):
        layout = self.layout
        self.asteroid = self.drawAsteroid(layout.asteroid)
        self.walls = layout.walls
        self.drawWalls(layout.walls) 
        pygame.display.flip()

    def isWall(self, x, y, walls):
        if x<0 or y<0:
            return False
        if x>=walls.width or y>=walls.height:
            return False
        return walls[x][y]

    def drawWalls(self, wallMatrix):
        for xNum, x in enumerate(wallMatrix):
            for yNum, cell in enumerate(x):
                if cell:
                    pos = (xNum, yNum)
                    screen = self.to_screen(pos)
                    self.screen.blit(self.wallImage, screen)

    def drawAsteroid(self, asteroidMatrix):
        asteroidImages = []
        for xNum, x in enumerate(asteroidMatrix):
            imageRow = []
            asteroidImages.append(imageRow)
            for yNum, cell in enumerate(x):
                if cell: # There's asteroid here
                    screen = self.to_screen((xNum, yNum))
                    imageRow.append((screen, self.asteroidImage))
                    self.screen.blit(self.asteroidImage, screen)

                else:
                    imageRow.append(None)

        return asteroidImages
        

    def drawAgentObjects(self, state):
        self.agentImages = []
        self.bulletImages = []
        for index, agent in enumerate(state.agentStates):
            if agent.isSpaceShip:  # Spaceship 
                image = self.drawSpaceShip(agent)
                self.agentImages.append((agent, image))
            elif agent.isUpBullet:
                image = self.drawUpBullet(agent)
                self.agentImages.append((agent, image))
            elif agent.isDownBullet:
                image = self.drawDownBullet(agent)
                self.agentImages.append((agent, image))
            else: #enemy
                image = self.drawEnemy(agent)
                self.agentImages.append((agent, image))

        pygame.display.flip()

    def drawSpaceShip(self, spaceship):
        position = self.getPosition(spaceship)
        screen_point = self.to_screen(position)
        self.screen.blit(self.spaceshipImage, screen_point)
        return self.spaceshipImage

    def drawEnemy(self, enemy):
        position = self.getPosition(enemy)
        screen_point = self.to_screen(position)
        self.screen.blit(self.enemyImage, screen_point)
        return self.enemyImage
    
    def drawUpBullet(self, bullet):
        position = self.getPosition(bullet)
        screen_point = self.to_screen(position)
        self.screen.blit(self.bulletImage, screen_point)
        return self.bulletImage
    
    def drawDownBullet(self, bullet):
        position = self.getPosition(bullet)
        screen_point = self.to_screen(position)
        self.screen.blit(self.rotatedBulletImage, screen_point)
        return self.rotatedBulletImage
    

    def moveSpaceShip(self, spaceship, prevSpaceship, image):
        prev_screen_pos = self.to_screen(self.getPosition(prevSpaceship))
        new_screen_pos = self.to_screen(self.getPosition(spaceship))
    
        self.screen.fill(BACKGROUND_COLOR, (*prev_screen_pos, self.gridSize, self.gridSize))
        self.screen.blit(image, new_screen_pos)

    def moveEnemy(self, enemy, prevEnemy, image):
        prev_screen_pos = self.to_screen(self.getPosition(prevEnemy))
        new_screen_pos = self.to_screen(self.getPosition(enemy))
    
        self.screen.fill(BACKGROUND_COLOR, (*prev_screen_pos, self.gridSize, self.gridSize))
        self.screen.blit(image, new_screen_pos)

    def moveUpBullet(self, bullet, prevBullet, image):
        prev_screen_pos = self.to_screen(self.getPosition(prevBullet))
        new_screen_pos = self.to_screen(self.getPosition(bullet))

        pvx, pvy = self.getPosition(prevBullet)
        nwx, nwy = self.getPosition(bullet)
        
        self.screen.fill(BACKGROUND_COLOR, (*prev_screen_pos, self.gridSize, self.gridSize))
        self.screen.blit(image, new_screen_pos)

    def moveDownBullet(self, bullet, prevBullet, image):
        prev_screen_pos = self.to_screen(self.getPosition(prevBullet))
        new_screen_pos = self.to_screen(self.getPosition(bullet))

        pvx, pvy = self.getPosition(prevBullet)
        nwx, nwy = self.getPosition(bullet)
        
        self.screen.fill(BACKGROUND_COLOR, (*prev_screen_pos, self.gridSize, self.gridSize))
        self.screen.blit(image, new_screen_pos)
            

    def finish(self):
        pygame.quit()

    def to_screen(self, point):
        (x, y) = point
        x = (x ) * self.gridSize 
        y = (y ) * self.gridSize 
        
        return (int(x), int(y))

    def getPosition(self, agentState):
        if agentState.configuration is None:
            return (-1000, -1000)
        return agentState.getPosition()

    def update(self, newState):
        agentIndex = newState._agentMoved
        
        for index in sorted(newState._agentDeleted, reverse=True):
            self.removeAgent(index)
        

        for index, killed in enumerate(newState._killed):
            if(killed):
                self.removeBlitImage(index)
                newState._killed[index] = False

        agentState = newState.agentStates[agentIndex]

        if agentState.isSpaceShip:  # Spaceship
            self.moveSpaceShip(agentState, self.agentImages[agentIndex][0], self.agentImages[agentIndex][1])
            self.agentImages[agentIndex] = (agentState, self.agentImages[agentIndex][1])
        
        elif agentState.isUpBullet: 
            if self.agentImages[agentIndex] is not None:
                self.moveUpBullet(agentState, self.agentImages[agentIndex][0], self.agentImages[agentIndex][1])
                self.agentImages[agentIndex] = (agentState, self.agentImages[agentIndex][1])
        elif agentState.isDownBullet: 
            if self.agentImages[agentIndex] is not None:
                self.moveDownBullet(agentState, self.agentImages[agentIndex][0], self.agentImages[agentIndex][1])
                self.agentImages[agentIndex] = (agentState, self.agentImages[agentIndex][1])
        else: # Enemy
            if self.agentImages[agentIndex] is not None:
                self.moveEnemy(agentState, self.agentImages[agentIndex][0], self.agentImages[agentIndex][1])
                self.agentImages[agentIndex] = (agentState, self.agentImages[agentIndex][1])

        
        if newState._asteroidEaten != None:
            self.removeAsteroid(newState._asteroidEaten, self.asteroid)


        self.drawScore(newState.score)
        self.drawAgentObjects(newState)
        self.drawWalls(self.walls)
        self.drawAsteroid(newState.asteroid)
        pygame.display.flip()


    def removeAsteroid(self, cell, asteroidImages):
        x, y = cell
        screen_pos = self.to_screen(cell)
        self.screen.fill(BACKGROUND_COLOR, (*screen_pos, self.gridSize, self.gridSize))
        asteroidImages[x][y] = None

    def removeBlitImage(self, index):
        if index >= len(self.agentImages):
            return 
        if self.agentImages[index] is not None:
            agent, image = self.agentImages[index]
            position = self.getPosition(agent)
            screen_pos = self.to_screen(position)
            self.screen.fill(BACKGROUND_COLOR, (*screen_pos, self.gridSize, self.gridSize))

    def removeAgent(self, index):
        if index >= len(self.agentImages):
            return
        if self.agentImages[index] is not None:
            agent, image = self.agentImages[index]
            position = self.getPosition(agent)
            screen_pos = self.to_screen(position)
            self.screen.fill(BACKGROUND_COLOR, (*screen_pos, self.gridSize, self.gridSize))
        
        del self.agentImages[index]
        
    
    def removeBullet(self, bindex):
        if bindex >= len(self.bulletImages):
            return
        if self.bulletImages[bindex] is not None:
            agent, image = self.bulletImage[bindex]
            position = self.getPosition(agent)
            screen_pos = self.to_screen(position)
            self.screen.fill(BACKGROUND_COLOR, (*screen_pos, self.gridSize, self.gridSize))
        
        del self.bulletImages[bindex]

    def drawScore(self, score):
        self.screen.fill(BACKGROUND_COLOR, (10, self.screen_height - INFO_PANE_HEIGHT + 10, 150, 36))
        pygame.font.init()
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(text, (10, self.screen_height - INFO_PANE_HEIGHT + 10))

