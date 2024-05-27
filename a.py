import random  # For generating random numbers
import sys  # We will use sys.exit to exit the program
import pygame
from pygame.locals import *  # Basic pygame imports
import mysql.connector  # MySQL connector

# Global Variables for the game
FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'

# Initialize Pygame
pygame.init()
FPSCLOCK = pygame.time.Clock()
pygame.display.set_caption('FEATHER FRENZY')

# Load game assets
GAME_SPRITES['numbers'] = (
    pygame.image.load('gallery/sprites/0.png').convert_alpha(),
    pygame.image.load('gallery/sprites/1.png').convert_alpha(),
    pygame.image.load('gallery/sprites/2.png').convert_alpha(),
    pygame.image.load('gallery/sprites/3.png').convert_alpha(),
    pygame.image.load('gallery/sprites/4.png').convert_alpha(),
    pygame.image.load('gallery/sprites/5.png').convert_alpha(),
    pygame.image.load('gallery/sprites/6.png').convert_alpha(),
    pygame.image.load('gallery/sprites/7.png').convert_alpha(),
    pygame.image.load('gallery/sprites/8.png').convert_alpha(),
    pygame.image.load('gallery/sprites/9.png').convert_alpha(),
)
GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
                        pygame.image.load(PIPE).convert_alpha())
GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')
GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
GAME_SPRITES['gameover'] = pygame.image.load('gallery/sprites/gameover.png').convert_alpha()
GAME_SPRITES['menu_message'] = pygame.image.load('gallery/sprites/menu_message.png').convert_alpha()
GAME_SPRITES['pause'] = pygame.image.load('gallery/sprites/pause.png').convert_alpha()
GAME_SPRITES['play'] = pygame.image.load('gallery/sprites/play.png').convert_alpha()

# Game states
MENU = 0
PLAYING = 1
LEADERBOARD = 2
game_state = MENU

# Game variables
sound_on = True
leaderboard = []
player_name = ''

# MySQL connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="flappybird"
    )

def insert_score(name, score):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leaderboard (name, score) VALUES (%s, %s)", (name, score))
    conn.commit()
    cursor.close()
    conn.close()

def fetch_leaderboard():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 5")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def menu_screen():
    global game_state, sound_on

    # Load menu option images
    start_game_img = pygame.image.load('gallery/sprites/start_game.png').convert_alpha()
    sound_on_img = pygame.image.load('gallery/sprites/sound_on.png').convert_alpha()
    sound_off_img = pygame.image.load('gallery/sprites/sound_off.png').convert_alpha()
    leaderboard_img = pygame.image.load('gallery/sprites/leaderboard.png').convert_alpha()
    exit_img = pygame.image.load('gallery/sprites/exit.png').convert_alpha()

    while game_state == MENU:
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        
        SCREEN.blit(GAME_SPRITES['menu_message'], (10, 20))

        # Blit menu option images
        SCREEN.blit(start_game_img, (20, 160))
        if sound_on:
            SCREEN.blit(sound_on_img, (20, 220))
        else:
            SCREEN.blit(sound_off_img, (20, 220))
        SCREEN.blit(leaderboard_img, (20, 280))
        SCREEN.blit(exit_img, (20, 340))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                game_state = PLAYING
            elif event.type == KEYDOWN and event.key == K_s:
                sound_on = not sound_on
            elif event.type == KEYDOWN and event.key == K_l:
                game_state = LEADERBOARD

def leaderboard_screen():
    global game_state
    font = pygame.font.Font(None, 28)
    leaderboard_data = fetch_leaderboard()
    while game_state == LEADERBOARD:
        SCREEN.fill((0, 0, 0))
        draw_text('Leaderboard', font, (255, 255, 255), SCREEN, 70, 50)
        for i, (name, score) in enumerate(leaderboard_data):
            draw_text(f'{i + 1}. {name}: {score}', font, (255, 255, 255), SCREEN, 70, 100 + i * 30)
        draw_text('Back to Menu (Press B)', font, (255, 255, 255), SCREEN, 20, 450)
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_b:
                game_state = MENU

def get_player_name():
    global player_name
    font = pygame.font.Font(None, 28)
    input_box = pygame.Rect(50, 200, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    show_text = False
    text = ''
    
    while not player_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        player_name = text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        SCREEN.fill((0, 0, 0))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        SCREEN.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(SCREEN, color, input_box, 2)
        
        draw_text('Enter your name:', font, (255, 255, 255), SCREEN, 50, 150)

        
        pygame.display.flip()
        FPSCLOCK.tick(30)

def welcomeScreen():
    """
    Shows welcome images on the screen
    """
    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0
    show_text =True
    font = pygame.font.Font(None,28)
     
    while True:
        for event in pygame.event.get():
            # if user clicks on cross button, close the game
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # If the user presses space or up key, start the game for them
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'], (0, 0))
                SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
                SCREEN.blit(GAME_SPRITES['message'], (messagex,messagey ))
                SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
                if show_text:
                    draw_text("Press SPACE or UP to Start", font, (255, 255, 255), SCREEN, 50, SCREENHEIGHT * 0.75)
                show_text = not show_text  # Toggle the show_text variable every frame
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    global game_state
    global leaderboard
    global sound_on
    score = 0
    level = 1
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENWIDTH / 2)
    basex = 0
    font = pygame.font.Font(None, 28)
    paused = False  # Initialize pause state
    pause_button_rect = GAME_SPRITES['pause'].get_rect(topleft=(SCREENWIDTH - 50, 10))
    play_button_rect = GAME_SPRITES['play'].get_rect(topleft=(SCREENWIDTH - 50, 10))

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    # List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -8
    playerFlapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    if sound_on:
                        GAME_SOUNDS['wing'].play()
            # Pause game if pause button is clicked
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if pause_button_rect.collidepoint(mouse_pos) and not paused:
                    paused = True
                    pygame.mixer.pause()
                elif play_button_rect.collidepoint(mouse_pos) and paused:
                    paused = False
                    pygame.mixer.unpause()

        if paused:
            SCREEN.blit(GAME_SPRITES['play'], play_button_rect.topleft)
            pygame.display.update()
            continue  # Skip the rest of the loop if the game is paused

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)  # This function will return true if the player is crashed
        if crashTest:
            insert_score(player_name, score)
            leaderboard.append(score)
            leaderboard = sorted(leaderboard, reverse=True)[:5]
           
            SCREEN.blit(GAME_SPRITES['gameover'], (50, 180))  # Display game over image
            draw_text(f'Your Score: {score}', font, (255, 255, 255), SCREEN, 100, 300)  # Display final score
            pygame.display.update()
            pygame.time.delay(2000)
            
            game_state = MENU
            return

        # Check for score and level up
        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1  # Increment score for passing each pipe
                if score % 10 == 0:  # Increment level every time score reaches a multiple of 10
                    level += 1
                if sound_on:
                    GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # Move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # If the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Let's blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        # Display level
        level_text = font.render(f'Level: {level}', True, (255, 255, 255))
        SCREEN.blit(level_text, (10, 10))

        # Display pause button
        SCREEN.blit(GAME_SPRITES['pause'], pause_button_rect.topleft)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return True

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    """
    Generate positions of two pipes(one bottom straight and one top rotated ) for blitting on the screen
    """
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  # upper Pipe
        {'x': pipeX, 'y': y2}  # lower Pipe
    ]
    return pipe

def main():
    global game_state
    while True:
        if game_state == MENU:
            menu_screen()
        elif game_state == LEADERBOARD:
            leaderboard_screen()
        elif game_state == PLAYING:
            get_player_name()
            welcomeScreen()
            mainGame()

if __name__ == "__main__":
    main()
