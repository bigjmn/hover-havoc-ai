import math 
import pygame

WIDTH = 700 
HEIGHT = 700 
DRAG = 0.98 
BOUNCE = 1.5

HOVER_CRAFT_RADIUS = 30
BALL_RADIUS = 15

COLOR_MAP = {
    "green": {
        "primary": (31,137,26),
        "secondary": (31,137,26,.5)
    },
    "orange": {
        "primary": (223,118,27),
        "secondary": (223,118,27,.5)
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
        left_bound = self.radius 
        top_bound = self.radius 
        bottom_bound = HEIGHT - self.radius 
        right_bound = WIDTH - self.radius 
        self.posX += self.velX 
        if self.posX >= right_bound:
            self.posX = 2*right_bound-self.posX 
            self.velX = -self.velX*BOUNCE 
        if self.posX <= left_bound:
            self.posX = 2*left_bound-self.posX 
            self.velX =-self.velX*BOUNCE 
        self.posY += self.velY 
        if self.posY >= bottom_bound:
            self.posY = 2*bottom_bound-self.posY 
            self.velY = -self.velY*BOUNCE 
        if self.posY <= top_bound:
            self.posY = 2*top_bound-self.posY
            self.velY = -self.velY*BOUNCE 
        self.velX*=DRAG 
        self.velY*=DRAG 

    #this must be overridden in subclasses 
    def draw_to_screen(self, screen):
        raise NotImplementedError("subclass must have draw method")
        

    
    
class HoverCraft(Mover):
    def __init__(self, name, posX, posY, velX, velY, theta):
        super().__init__(name, posX, posY, velX, velY, HOVER_CRAFT_RADIUS)
        #angle relative to the horizontal 
        self.theta = theta
        self.color = name 
        self.isThrusting = False 
        # will be 1, 0, or -1 
        self.angleChange = 0
    
    def turnClock(self):
        self.theta += math.pi/80

    def turnCounterClock(self):
        self.theta -= math.pi/80

    def thrust(self):
        # with drag, max velocity is 10 
        self.velX += math.cos(self.theta)*.2
        self.velY += math.sin(self.theta)*.2

    def handle_input(self, input_vec):
        self.angleChange = 0
        if input_vec[0] == 1:
            self.angleChange = 1 
        if input_vec[2] == 1:
            self.angleChange = -1
        if input_vec[0] == 1 and input_vec[2] == 1:
            self.angleChange = 0 

        self.isThrusting = (input_vec[1] == 1)

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
    def border_points(self):
        return polygon_points(self.posX, self.posY, self.radius, self.theta)
    @property 
    def tail_center(self):
        tailX = self.posX + math.cos(self.theta+math.pi)*(self.radius)
        tailY = self.posY + math.sin(self.theta+math.pi)*(self.radius)
        return [tailX, tailY]
    
    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, COLOR_MAP[self.color]["primary"], [self.posX, self.posY], self.radius)
        pygame.draw.polygon(screen, COLOR_MAP[self.color]["secondary"], self.border_points)

class Ball(Mover):
    def __init__(self, posX, posY, velX, velY):
        super().__init__("Ball", posX, posY, velX, velY, BALL_RADIUS)
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
        return dc
    
    def draw_to_screen(self, screen):
        pygame.draw.circle(screen, "black", [self.posX, self.posY], self.radius+3)
        pygame.draw.circle(screen, self.draw_color, [self.posX, self.posY], self.radius)

# resolve movers bouncing 
def resolve_bounce(comp1, comp2):
    assert isinstance(comp1, Mover) and isinstance(comp2, Mover)    
    net_velX_change = comp2.velX - comp1.velX 
    net_velY_change = comp2.velY - comp1.velY 

    comp1.velX = BOUNCE*net_velX_change/2 
    comp1.velY = BOUNCE*net_velY_change/2 

    comp2.velX = -BOUNCE*net_velX_change/2 
    comp2.velY = -BOUNCE*net_velY_change/2 

def determine_bounce(comp1, comp2):

    assert isinstance(comp1, Mover) and isinstance(comp2, Mover)    
    total_dist = math.sqrt((comp1.posX-comp2.posX)**2+(comp1.posY-comp2.posY)**2)
    if total_dist <= comp1.radius+comp2.radius:
        return True 
    return False 

class Game:
    def __init__(self):
        
        self.orangeCraft = HoverCraft("orange", 300, 300, 0, 0, 0)
        self.greenCraft = HoverCraft("green", 900, 900, 0, 0, 3*math.pi/2)
        self.ball = Ball(600, 600, 0, 0)

        self.orange_ticker = 0 
        self.green_ticker = 0

    @property
    def posession_color(self):
        return self.ball.color 
    @property
    def all_components(self):
        return [self.orangeCraft, self.greenCraft, self.ball]
    
    def update_components(self):
        if determine_bounce(self.orangeCraft, self.greenCraft):
            resolve_bounce(self.orangeCraft, self.greenCraft)
        if determine_bounce(self.orangeCraft, self.ball):
            self.ball.change_color("orange") 
            resolve_bounce(self.orangeCraft, self.ball)
        if determine_bounce(self.greenCraft, self.ball):
            
            self.ball.change_color("green")
            resolve_bounce(self.greenCraft, self.ball)

        for comp in self.all_components:
            comp.move()

    def resolve_tick(self, orangeInput, greenInput):
        if self.posession_color == "green":
            self.green_ticker += 1 
        if self.posession_color == "orange":
            self.orange_ticker += 1

        self.orangeCraft.handle_input(orangeInput)
        self.greenCraft.handle_input(greenInput)

        self.update_components()

    # for drawing 
    def draw_components(self, screen):
        for comp in self.all_components:
            comp.draw_to_screen(screen)




def polygon_points(centerX, centerY, circle_rad, theta):
    front_offset_x = math.cos(theta+math.pi/2)*circle_rad
    front_offset_y = math.sin(theta+math.pi/2)*circle_rad
    center_back_x = centerX+math.cos(theta+math.pi)*2*circle_rad 
    center_back_y = centerY+math.sin(theta+math.pi)*2*circle_rad 

    front_right_x = centerX+front_offset_x 
    front_right_y = centerY+front_offset_y

    front_left_x = centerX - front_offset_x 
    front_left_y = centerY - front_offset_y 

    back_right_x = center_back_x+front_offset_x 
    back_right_y = center_back_y + front_offset_y 

    back_left_x = center_back_x - front_offset_x 
    back_left_y = center_back_y - front_offset_y 

    return [(front_right_x, front_right_y), 
            (front_left_x, front_left_y), 
            (back_left_x, back_left_y), 
            (back_right_x, back_right_y)]
    