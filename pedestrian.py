import pygame
import sys
import random
import math
import time
import os

pygame.init()
pygame.mixer.init()

# ================= pedestrian_simulation.py =================

WIDTH, HEIGHT = 900, 600
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Pedestrian Simulation")
clock = pygame.time.Clock()

background = pygame.image.load("background.png").convert()
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

player_image = pygame.image.load("character.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 50))

car_img = pygame.transform.scale(pygame.image.load("car.png").convert_alpha(), (80, 40))

up_button_img = pygame.transform.scale(pygame.image.load("up_button.png").convert_alpha(), (110, 110))
down_button_img = pygame.transform.scale(pygame.image.load("down_button.png").convert_alpha(), (120, 120))
retry_button_img = pygame.transform.scale(pygame.image.load("retry_button.png").convert_alpha(), (200, 80))
next_button_img = pygame.transform.scale(pygame.image.load("next_button.png").convert_alpha(), (100, 80))

red_light = pygame.transform.scale(pygame.image.load("traffic_red.png").convert_alpha(), (250, 320))
yellow_light = pygame.transform.scale(pygame.image.load("traffic_yellow.png").convert_alpha(), (250, 320))
green_light = pygame.transform.scale(pygame.image.load("traffic_green.png").convert_alpha(), (250, 320))
traffic_x, traffic_y = 180, -80

ped_red_light = pygame.transform.scale(pygame.image.load("ped_red.png").convert_alpha(), (190, 210))
ped_yellow_light = pygame.transform.scale(pygame.image.load("ped_yellow.png").convert_alpha(), (190, 210))
ped_green_light = pygame.transform.scale(pygame.image.load("ped_green.png").convert_alpha(), (190, 210))
ped_light_x, ped_light_y = 285, 75

horn_sound = pygame.mixer.Sound("car.mp3")
gameover_sound = pygame.mixer.Sound("over.mp3")
phone_sound = pygame.mixer.Sound("ring.mp3")
click_sound = pygame.mixer.Sound("tap.mp3")
success_sound = pygame.mixer.Sound("win.mp3")
traffic_sound = pygame.mixer.Sound("traffic.mp3")
traffic_sound.play(-1)

PLAYER_SIZE = 15
player_x, player_y = 400, 390
PLAYER_SPEED = 2
FINISH_Y = 90

vehicles = [
    {"x": -100, "y": 220, "dir": 1, "speed": 6},
    {"x": WIDTH+100, "y": 300, "dir": -1, "speed": 7}
]

CAR_GREEN, CAR_YELLOW, CAR_RED = 7, 3, 20
cycle = CAR_GREEN + CAR_YELLOW + CAR_RED
light_timer = 0

def car_light(t):
    t %= cycle
    if t < CAR_GREEN: return "GREEN"
    if t < CAR_GREEN + CAR_YELLOW: return "YELLOW"
    return "RED"

def ped_light(t):
    return "GREEN" if car_light(t) == "RED" else "RED"

up_button_rect = pygame.Rect(50, 420, 120, 120)
down_button_rect = pygame.Rect(200, 420, 120, 120)
retry_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 80)
next_button_rect = pygame.Rect(WIDTH//2 - 60, HEIGHT//2 + 40, 250, 90)

pixel_font_small = pygame.font.Font("pixel_font.otf", 25)
pixel_font_big = pygame.font.Font("pixel_font.otf", 80)

move_forward = False
move_back = False
game_over = False
success = False
running = True

last_time = time.time()

while running:
    dt = time.time() - last_time
    last_time = time.time()
    light_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP): move_forward = True
            if event.key in (pygame.K_s, pygame.K_DOWN): move_back = True
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP): move_forward = False
            if event.key in (pygame.K_s, pygame.K_DOWN): move_back = False

    if move_forward: player_y -= PLAYER_SPEED * dt * 60
    if move_back: player_y += PLAYER_SPEED * dt * 60

    for v in vehicles:
        v["x"] += v["dir"] * v["speed"]
        if v["x"] > WIDTH+200: v["x"] = -200
        if v["x"] < -200: v["x"] = WIDTH+200

    if player_y <= FINISH_Y and not success:
        success = True
        success_sound.play()

    window.blit(background,(0,0))
    for v in vehicles:
        window.blit(car_img,(v["x"],v["y"]))
    window.blit(player_image,(player_x,player_y))

    if car_light(light_timer) == "RED":
        window.blit(red_light,(traffic_x,traffic_y))
        window.blit(ped_green_light,(ped_light_x,ped_light_y))
    else:
        window.blit(green_light,(traffic_x,traffic_y))
        window.blit(ped_red_light,(ped_light_x,ped_light_y))

    if success:
        window.blit(next_button_img, next_button_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

# ================= beepbeepSafety.py =================

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Good Job Screen")

current_folder = os.path.dirname(os.path.abspath(__file__))

pixel_font = pygame.font.Font(os.path.join(current_folder, "BoldPixels.ttf"), 100)
pixel_font_small = pygame.font.Font(os.path.join(current_folder, "BoldPixels.ttf"), 33)

def load_image(filename, scale=None):
    path = os.path.join(current_folder, filename)
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    return None

flashcard_bg = load_image("flashcardbackground2.png", (WIDTH, HEIGHT))
textbox_bg = load_image("yellowtextbox.png", (750, 450))
textbox_pos = ((WIDTH - 750)//2, (HEIGHT - 450)//2)

badge_img = load_image("buttonbadge.png", (150,150))
back_btn_rect = pygame.Rect(400, 400, 100, 100)
back_img = load_image("backmainmenu.png", (100,100))

def simulation_completed_page():
    running = True
    clock = pygame.time.Clock()
    badge_y = -150

    lines = [
        "Congrats! You have completed the quest",
        "in SafeVille!",
        "You have been rewarded the",
        "Road Rangers Badge!",
    ]
    rendered = [""]*len(lines)
    li = ci = 0

    while running:
        screen.fill((0,0,0))
        if flashcard_bg:
            screen.blit(flashcard_bg,(0,0))
        if textbox_bg:
            screen.blit(textbox_bg,textbox_pos)

        title = pixel_font.render("GOOD JOB!", True, (0,0,0))
        screen.blit(title,(225,110))

        if li < len(lines):
            if ci < len(lines[li]):
                rendered[li] = lines[li][:ci+1]
                ci += 1
            else:
                li += 1
                ci = 0

        for i,t in enumerate(rendered):
            screen.blit(pixel_font_small.render(t,True,(0,0,0)),(150,220+i*40))

        if badge_y < 290:
            badge_y += 6
        if badge_img:
            screen.blit(badge_img,(WIDTH//2+170,badge_y))

        screen.blit(back_img, back_btn_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn_rect.collidepoint(event.pos):
                    running = False

        pygame.display.update()
        clock.tick(60)

simulation_completed_page()
sys.exit()
