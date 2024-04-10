import math 
import pygame
WIDTH = 100 
HEIGHT = 100 
DRAG = 0.9 
BOUNCE = 1.1

COLOR_MAP = {
    "blue": {
        "primary": (0,0,255),
        "secondary": (0,0,255,.5)
    },
    "orange": {
        "primary": (255,160,0),
        "secondary": (255,160,0,.5)
    }
}

# basic physics relating to both the hover crafts and ball
class Mover:
    def __init__(self, name, posX, posY, velX, velY, radius):
        self.name = name 
        self.posX = posX
        self.posY = posY 
        self.velX = velX 
        self.velY = velY 
        self.radius = radius 

    def resolve_drift(self):
        self.posX += self.velX 
        if self.posX >= WIDTH:
            self.posX = 2*WIDTH-self.posX 
            self.velX = -self.velX*BOUNCE 
        if self.posX <= 0:
            self.posX = -self.posX 
            self.velX =-self.velX*BOUNCE 
        self.posY += self.velY 
        if self.posY >= HEIGHT:
            self.posY = 2*HEIGHT-self.posY 
            self.velY = -self.velY*BOUNCE 
        if self.posY <= 0:
            self.posY = -self.posY
            self.velY = -self.velY*BOUNCE 
        self.velX*=DRAG 
        self.velY*=DRAG 

    
    
class HoverCraft(Mover):
    def __init__(self, name, posX, posY, velX, velY, theta):
        super().__init__(name, posX, posY, velX, velY, 2)
        #angle relative to the horizontal 
        self.theta = theta
        self.color = name 
        self.isThrusting = False 
        # will be 1, 0, or -1 
        self.angleChange = 0
    
    def turnClock(self):
        self.theta += math.pi/20

    def turnCounterClock(self):
        self.theta -= math.pi/20

    def thrust(self):
        # with drag, max velocity is 10 
        self.velX += math.cos(self.theta)
        self.velY += math.sin(self.theta)

    def handle_input(self, input_vec):
        if input_vec[0] == 1:
            self.angleChange = 1 
        if input_vec[2] == 1:
            self.angleChange = -1
        if input_vec[0] == 1 and input_vec[2] == 1:
            self.angleChange = 0 

        self.isThrusting = (input_vec[0] == 1)

    # the order of updates shouldn't matter as long as the timestep is small
    def move(self):
        if self.isThrusting:
            self.thrust()
        if self.angleChange == 1:
            self.turnClock()
        if self.angleChange == -1:
            self.turnCounterClock()
        self.resolve_drift()

    # for drawing 
    @property 
    def tail_center(self):
        tailX = self.posX + math.cos(self.theta+math.pi)*(self.radius/2)
        tailY = self.posY + math.sin(self.theta+math.pi)*(self.radius/2)
        return [tailX, tailY]
    
    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, COLOR_MAP[self.color]["primary"], [self.posX, self.posY], self.radius)
        pygame.draw.circle(screen, COLOR_MAP[self.color]["secondary"], self.tail_center, self.radius)

class Ball(Mover):
    def __init__(self, posX, posY, velX, velY):
        super().__init__("Ball", posX, posY, velX, velY, 1)
        self.color = None 

    def change_color(self, color):
        self.color = color 
        
    def move(self):
        self.resolve_drift()

    # for drawing 
    @property 
    def draw_color(self):
        # default
        dc = "gray"
        if self.color:
            dc = COLOR_MAP[self.color]["primary"]
        return self.color 
    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, "black", [self.posX, self.posY], self.radius+3)
        pygame.draw.circle(screen, self.draw_color, [self.posX, self.posY, self.radius])

class Game:
    def __init__(self):
        
        self.orangeCraft = HoverCraft("orange", 30, 30, 0, 0, 0)
        self.blueCraft = HoverCraft("blue", 80, 80, 0, 0, 3*math.pi/2)
        self.ball = Ball(50, 50, 0, 0)

        self.orange_ticker = 0 
        self.blue_ticker = 0

    @property
    def posession_color(self):
        return self.ball.color 
    @property
    def all_components(self):
        return [self.orangeCraft, self.blueCraft, self.ball]
    
    def resolve_bounce(comp1, comp2):
        net_velX_change = comp2.velX - comp1.velX 
        net_velY_change = comp2.velY - comp1.velY 

        comp1.velX = BOUNCE*net_velX_change/2 
        comp1.velY = BOUNCE*net_velY_change/2 

        comp2.velX = -BOUNCE*net_velX_change/2 
        comp2.velY = -BOUNCE*net_velY_change/2 

    def determine_bounce(comp1, comp2):
        total_dist = math.sqrt((comp1.posX-comp2.posX)**2+(comp1.posY-comp2.posY)**2)
        if total_dist <= comp1.radius+comp2.radius:
            return True 
        return False 
    
    def update_components(self):
        if self.determine_bounce(self.orangeCraft, self.blueCraft):
            self.resolve_bounce(self.orangeCraft, self.blueCraft)
        if self.determine_bounce(self.orangeCraft, self.ball):
            self.ball.change_color("orange") 
            self.resolve_bounce(self.orangeCraft, self.ball)
        if self.determine_bounce(self.blueCraft, self.ball):
            
            self.ball.change_color("blue")
            self.resolve_bounce(self.orangeCraft, self.ball)

        for comp in self.all_components:
            comp.move()

    def resolve_tick(self, orangeInput, blueInput):
        if self.posession_color == "blue":
            self.blue_ticker += 1 
        if self.posession_color == "orange":
            self.orange_ticker += 1

        self.orangeCraft.handle_input(orangeInput)
        self.blueCraft.handle_input(blueInput)

        self.update_components()





    