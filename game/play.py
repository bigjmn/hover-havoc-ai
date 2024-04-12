import pygame 

from game_logic import HoverCraft, Ball, Game, WIDTH, HEIGHT 

def control_state(keystate, clock_turn_key, thrust_key, counterclock_turn_key):
    clock_turn_val = 1 if keystate[clock_turn_key] else 0 
    thrust_val = 1 if keystate[thrust_key] else 0 
    counterclock_val = 1 if keystate[counterclock_turn_key] else 0 
    return [clock_turn_val, thrust_val, counterclock_val]
def inputVecs():
    keystate = pygame.key.get_pressed()
    orange_inputs = control_state(keystate, pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT)
    green_inputs = control_state(keystate, pygame.K_d, pygame.K_w, pygame.K_a)
    return orange_inputs, green_inputs

def run_game():
    game = Game()
    pygame.init()

    screen = pygame.display.set_mode([1100, 1100])
    play_area = pygame.display.get_surface().subsurface(100, 100, WIDTH, HEIGHT)


    # loop until close 
    done = False 
    clock = pygame.time.Clock()
    pyfont = pygame.font.Font(pygame.font.get_default_font(), 42)

    while not done: 
        screen.fill((47,121,140))
        play_area.fill((103,189,211))
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True 

        orange_inputs, green_inputs = inputVecs()
        game.resolve_tick(orange_inputs, green_inputs)

        game.draw_components(play_area)

        #draw scores 
        orangeScore = str(game.orange_ticker//60).zfill(2)
        greenScore = str(game.green_ticker//60).zfill(2)
        greenSurf = pygame.font.Font.render(pyfont, greenScore, True, "green", (103,189,211))


        orangeSurf = pygame.font.Font.render(pyfont, orangeScore, True, "orange", (103,189,211))

        # orangeSurf = pygame.font.Font().render(orangeScore, True, "orange", background=(103,189,211))
        # greenSurf = pygame.font.Font().render(greenScore, True, "green", background=(103,189,211))

        pygame.display.get_surface().blit(orangeSurf, (WIDTH/2, 150+HEIGHT))
        pygame.display.get_surface().blit(greenSurf, (WIDTH/2+200, 150+HEIGHT))

        

        pygame.display.flip()

    pygame.quit()

run_game()


