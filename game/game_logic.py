import math 
import pygame

WIDTH = 700 
HEIGHT = 700 
DRAG = 0.98 
BOUNCE = 1.5

#this is the collision circle radius, graphic extends a bit further 
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

        # save start conditions for reset 
        self.start_posX = posX 
        self.start_posY = posY 
        self.start_velX = velX 
        self.start_velY = velY 

    # moves object based on inertia, handle wall bounces
    def resolve_drift(self):
        left_bound = self.radius 
        top_bound = self.radius 
        bottom_bound = HEIGHT - self.radius 
        right_bound = WIDTH - self.radius 
        self.posX += self.velX 

        # handle wall bounce 
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

        # velocity decays (but might be higher overall based on bounces/input)
        self.velX*=DRAG 
        self.velY*=DRAG 

    # methods that must be implemented in subclasses 
    def move(self):
        raise NotImplementedError("subclass must have move method")
    def reset_component(self):
        raise NotImplementedError("subclass must have reset method")
    
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

        # initials for resetting 
        self.start_theta = theta 


        
        
    
    def turnClock(self):
        self.theta += math.pi/80 
        if self.theta >= 2*math.pi:
            self.theta -= 2*math.pi 

    def turnCounterClock(self):
        self.theta -= math.pi/80
        if self.theta < 0:
            self.theta += 2*math.pi

    def thrust(self):
        # terminal velocity would be 1, but bounces complicate it 
        # would be nice to have [-1, 1] domain, but it'll probably be scaled when encoding state space anyway
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

    # for training 
    def reset_component(self):
        self.posX = self.start_posX 
        self.posY = self.start_posY 
        self.velX = self.start_velX
        self.velY = self.start_velY 
        self.theta = self.start_theta 

        self.angleChange = 0 
        self.isThrusting = False 

    def describe(self):
        return [[self.posX, self.posY], [self.velX, self.velY], self.theta]


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

    #for training 
    def reset_component(self):
        self.posX = self.start_posX 
        self.posY = self.start_posY 
        self.velX = self.start_velX
        self.velY = self.start_velY 

        self.color = None 

    def describe(self):
        return [[self.posX, self.posY], [self.velX, self.velY]]
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
    
    def get_component(self, name):
        if name == "orange":
            return self.orangeCraft 
        if name == "green":
            return self.greenCraft 
        if name == "ball":
            return self.ball 
        return None
    
    # encode having posession vs opponent having posession vs no one 
    def describe_posession(self, color):
        if self.posession_color == None:
            return 0 
        if self.posession_color == color:
            return 1 
        return -1 
    
    def check_termination(self):
        # returns both if the game is over, and the winner name 
        if self.orange_ticker >= 3600:
            return True, "orange"
        if self.green_ticker >= 3600:
            return True, "green"
        return False, None 
    
    def reset_game(self):
        for comp in self.all_components:
            assert isinstance(comp, Mover)
            comp.reset_component()

        self.orange_ticker = 0 
        self.green_ticker = 0

    
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
            assert isinstance(comp, Mover)
            comp.move()
            

    def resolve_tick(self, orangeInput, greenInput):
        if self.posession_color == "green":
            self.green_ticker += 1 
        if self.posession_color == "orange":
            self.orange_ticker += 1

        self.orangeCraft.handle_input(orangeInput)
        self.greenCraft.handle_input(greenInput)

        self.update_components()
    
    # for training 

    def score_order(self, color):
        if color == "orange": return [self.orange_ticker, self.green_ticker]
        if color == "green": return [self.green_ticker, self.orange_ticker]
        raise ValueError("color must be orange or green")
    # get observation from specific player (color) view
    def observe_from(self, color):
        opp_color = opponent_color(color)
        
    # for drawing 
    def draw_components(self, screen):
        for comp in self.all_components:
            assert isinstance(comp, Mover)
            comp.draw_to_screen(screen)


# basic helper for designating self vs opponent 
def opponent_color(color):
    if color == "orange": return "green"
    if color == "green": return "orange" 
    raise ValueError("not a recognized color")

# draw a rectangle angled at theta, centerX centerY is the middle of the "front"
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
    