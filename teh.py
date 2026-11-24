import pygame
import sys
import random
import math
import time

pygame.init()
pygame.mixer.init()


# -------------- WINDOW --------------
WIDTH, HEIGHT = 900, 600
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Pedestrian Simulation")
clock = pygame.time.Clock()

# -------------- ASSETS --------------
background = pygame.image.load("background.png").convert()
background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))

player_image = pygame.image.load("character.png").convert_alpha()
player_image = pygame.transform.scale(player_image, (50, 50))

car_img = pygame.transform.scale(pygame.image.load("orangecar.png").convert_alpha(), (80, 40))

up_button_img = pygame.transform.scale(pygame.image.load("up_button.png").convert_alpha(), (110, 110))
down_button_img = pygame.transform.scale(pygame.image.load("down_button.png").convert_alpha(), (120, 120))
retry_button_img = pygame.transform.scale(pygame.image.load("retry_button.png").convert_alpha(), (200, 80))
next_button_img = pygame.transform.scale(pygame.image.load("next_btn.png").convert_alpha(), (100, 80))

red_light = pygame.transform.scale(pygame.image.load("traffic_red.png").convert_alpha(), (250, 320))
yellow_light = pygame.transform.scale(pygame.image.load("traffic_yellow.png").convert_alpha(), (250, 320))
green_light = pygame.transform.scale(pygame.image.load("traffic_green.png").convert_alpha(), (250, 320))
traffic_x, traffic_y = 180, -80

ped_red_light = pygame.transform.scale(pygame.image.load("ped_red.png").convert_alpha(), (190, 210))
ped_yellow_light = pygame.transform.scale(pygame.image.load("ped_yellow.png").convert_alpha(), (190, 210))
ped_green_light = pygame.transform.scale(pygame.image.load("ped_green.png").convert_alpha(), (190, 210))
ped_light_x, ped_light_y = 285, 75

# -------------- SOUNDS --------------
pygame.mixer.init()
horn_sound = pygame.mixer.Sound("car.mp3")
gameover_sound = pygame.mixer.Sound("over.mp3")
phone_sound = pygame.mixer.Sound("ring.mp3")
phone_sound.set_volume(0.3)
click_sound = pygame.mixer.Sound("click.wav")
success_sound = pygame.mixer.Sound("win.mp3")
success_sound.set_volume(0.4)
traffic_sound = pygame.mixer.Sound("traffic.wav")
traffic_sound.set_volume(1.0)
traffic_sound.play(-1)  # loop indefinitely
rain_sound = pygame.mixer.Sound("rain.mp3")
rain_sound.set_volume(0.8)

# -------------- GAME AREA & CROSSING --------------
PLAYER_SIZE = 15
player_start_x = 400
player_start_y = 390
player_x = player_start_x
player_y = player_start_y
PLAYER_SPEED = 2

FINISH_Y = 90
CROSSING_START_Y = 250
CROSSING_END_Y = 280
CROSSING_X = WIDTH // 2 - 140
CROSSING_W = 280
STOP_LINE_LEFT = CROSSING_X - 8
STOP_LINE_RIGHT = CROSSING_X + CROSSING_W + 8

# -------------- VEHICLES --------------
VEHICLE_TYPES = [("car", car_img, 80, 40)]
LANE_TOP = 180
LANE_BOTTOM = 320
vehicles = []

def spawn_vehicles():
    vehicles.clear()
    v_type, img, w, h = VEHICLE_TYPES[0]

    # Top lane
    lane_y = LANE_TOP
    direction = 1
    x_pos = -100
    img_final = img if direction == 1 else pygame.transform.flip(img, True, False)
    speed = random.uniform(5.0, 8.0)
    vehicles.append({"x": x_pos, "y": lane_y, "speed": speed, "dir": direction, "img": img_final, "w": w, "h": h, "stopped": False})

    # Bottom lane
    lane_y = LANE_BOTTOM
    direction = -1
    x_pos = WIDTH + 100
    img_final = img if direction == 1 else pygame.transform.flip(img, True, False)
    speed = random.uniform(6.0, 9.0)
    vehicles.append({"x": x_pos, "y": lane_y, "speed": speed, "dir": direction, "img": img_final, "w": w, "h": h, "stopped": False})

spawn_vehicles()

# -------------- UI BUTTONS & TOGGLES --------------
up_button_rect = pygame.Rect(50, 420, 120, 120)
down_button_rect = pygame.Rect(200, 420, 120, 120)
retry_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 40, 200, 80)
next_button_rect = next_button_img.get_rect(
    center=(WIDTH//2, HEIGHT//2 + 80)
)

TOGGLE_WIDTH = 100
TOGGLE_HEIGHT = 40
TOGGLE_RADIUS = 10
pygame.init()
toggle_font = pygame.font.Font("pixel_font.otf", 20)
TOGGLE_ACTIVE_COLOR = (80, 180, 80)
TOGGLE_INACTIVE_COLOR = (200, 200, 200)
TOGGLE_TEXT_COLOR = (10, 10, 10)
TOGGLE_BORDER_COLOR = (50, 50, 50)
TOGGLE_BORDER_WIDTH = 2

toggle_buttons = {
    "day": pygame.Rect(20, 20, TOGGLE_WIDTH, TOGGLE_HEIGHT),
    "night": pygame.Rect(140, 20, TOGGLE_WIDTH, TOGGLE_HEIGHT),
    "rain": pygame.Rect(260, 20, TOGGLE_WIDTH, TOGGLE_HEIGHT),
    "light": pygame.Rect(380, 20, TOGGLE_WIDTH, TOGGLE_HEIGHT)
}

# -------------- TRAFFIC LIGHTS --------------
CAR_GREEN = 7.0
CAR_YELLOW = 3.0
CAR_RED = 20.0
cycle_length = CAR_GREEN + CAR_YELLOW + CAR_RED
car_light_timer = 0.0

def car_light_state(t):
    t = t % cycle_length
    if t < CAR_GREEN: return "GREEN"
    if t < CAR_GREEN + CAR_YELLOW: return "YELLOW"
    return "RED"

def ped_light_state(t):
    s = car_light_state(t)
    if s == "RED": return "GREEN"
    if s == "YELLOW": return "YELLOW"
    return "RED"

# -------------- RAIN --------------
RAIN_PARTICLES = []
MAX_RAIN = 500

def spawn_rain():
    while len(RAIN_PARTICLES) < MAX_RAIN:
        for _ in range(6):
            x = random.randint(0, WIDTH)
            y = random.randint(-140, -10)
            speed = random.uniform(4.0, 10.0)
            length = random.randint(8, 18)
            RAIN_PARTICLES.append([x, y, speed, length])

def update_rain(dt):
    for drop in RAIN_PARTICLES:
        drop[1] += drop[2] * dt * 60
        drop[0] += math.sin(pygame.time.get_ticks() * 0.001 + drop[0]) * 0.2
    while RAIN_PARTICLES and RAIN_PARTICLES[0][1] > HEIGHT + 50:
        RAIN_PARTICLES.pop(0)

def draw_rain(surf):
    for drop in RAIN_PARTICLES:
        x, y, speed, length = drop
        pygame.draw.line(surf, (170, 170, 200), (x, y), (x, y+length), 1)

# -------------- PHONE EVENT ----------------
PHONE_EVENT_CHANCE = 1.0
PHONE_RING_DURATION = 3.0
PHONE_DELAY_AFTER_CROSSING = 0.1

phone_active = False
phone_timer = 0.0
phone_event_triggered = False
phone_choice = None
player_entered_crossing = False
crossing_enter_time = None

# -------------- GREEN LIGHT TIMER ----------------
GREEN_TIMER_START = 20.0
green_timer = GREEN_TIMER_START
green_timer_running = False

# -------------- GAME STATE ----------------
game_over = False
game_over_msg = ""
show_retry = False
success = False
hover_next_played = False

pixel_font_small = pygame.font.Font("pixel_font.otf", 25)
pixel_font_big = pygame.font.Font("pixel_font.otf", 80)

move_forward = False
move_back = False

is_night = False
is_rain = False
headlights_on = False

bob_offset = 0.0
bob_dir = 1.0

# -------------- UTILITIES ----------------
def draw_hoverable_button(surface, rect, image, scale_factor=1.1):
    mx,my = pygame.mouse.get_pos()
    hovered = rect.collidepoint((mx,my))
    if hovered:
        w,h = rect.size
        scaled_img = pygame.transform.smoothscale(
        image, (int(w * scale_factor), int(h * scale_factor))
        )
        scaled_rect = scaled_img.get_rect(center=rect.center)
        surface.blit(scaled_img, scaled_rect)
    else:
        normal_rect = image.get_rect(center=rect.center)
        surface.blit(image, rect)

def draw_hoverable_toggle(surface, rect, text, active, scale_factor=1.1):
    mx,my = pygame.mouse.get_pos()
    hovered = rect.collidepoint((mx,my))
    color = TOGGLE_ACTIVE_COLOR if active else TOGGLE_INACTIVE_COLOR
    if hovered:
        w,h = rect.size
        scaled_rect = pygame.Rect(0,0,int(w*scale_factor),int(h*scale_factor))
        scaled_rect.center = rect.center
        pygame.draw.rect(surface, color, scaled_rect, border_radius=TOGGLE_RADIUS)
        pygame.draw.rect(surface, TOGGLE_BORDER_COLOR, scaled_rect, width=TOGGLE_BORDER_WIDTH, border_radius=TOGGLE_RADIUS)
        txt_surf = toggle_font.render(text, True, TOGGLE_TEXT_COLOR)
        surface.blit(txt_surf, txt_surf.get_rect(center=scaled_rect.center))
    else:
        pygame.draw.rect(surface, color, rect, border_radius=TOGGLE_RADIUS)
        pygame.draw.rect(surface, TOGGLE_BORDER_COLOR, rect, width=TOGGLE_BORDER_WIDTH, border_radius=TOGGLE_RADIUS)
        txt_surf = toggle_font.render(text, True, TOGGLE_TEXT_COLOR)
        surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))

# ---------------- Player & Vehicle functions ----------------
def player_rect():
    return pygame.Rect(player_x-PLAYER_SIZE//2, player_y-PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE)

def vehicle_rect(v):
    return pygame.Rect(int(v["x"]), int(v["y"]), v["w"], v["h"])

def draw_vehicle_headlight(surf, v):
    if v["dir"] == 1:
        x0, y0 = v["x"]+v["w"], v["y"]+v["h"]//2
        cone = [(x0,y0-10),(x0+200,y0-60),(x0+200,y0+60),(x0,y0+10)]
    else:
        x0, y0 = v["x"], v["y"]+v["h"]//2
        cone = [(x0,y0-10),(x0-200,y0-60),(x0-200,y0+60),(x0,y0+10)]
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(s,(255,255,200,40),cone)
    surf.blit(s,(0,0))

def reset_all():
    global player_x, player_y, game_over, game_over_msg, show_retry, success
    global phone_active, phone_timer, phone_event_triggered, phone_choice, car_light_timer
    global player_entered_crossing, green_timer, green_timer_running, is_rain
    player_x = player_start_x
    player_y = player_start_y
    game_over = False
    game_over_msg = ""
    show_retry = False
    success = False
    phone_active = False
    phone_timer = 0.0
    phone_event_triggered = False
    phone_choice = None
    car_light_timer = 0.0
    player_entered_crossing = False
    green_timer = GREEN_TIMER_START
    green_timer_running = False
    spawn_vehicles()
    if is_rain:
        rain_sound.play(-1)
    else:
        rain_sound.stop()

# ---------------- MAIN LOOP ----------------
running = True
last_time = time.time()

while running:
    now = time.time()
    dt_seconds = now - last_time
    last_time = now

    # adjust ambient sounds volume
    if is_night:
        traffic_sound.set_volume(1.0)
    elif is_rain:
        traffic_sound.set_volume(0.8)
    else:
        traffic_sound.set_volume(1.0)

    if is_rain and not pygame.mixer.get_busy():
        rain_sound.play(-1)
    elif not is_rain:
        rain_sound.stop()

    car_light_timer += dt_seconds

    # ---- input ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = pygame.mouse.get_pos()
            if toggle_buttons["day"].collidepoint((mx,my)):
                is_night = False
                click_sound.play()
            if toggle_buttons["night"].collidepoint((mx,my)):
                is_night = True
                click_sound.play()
            if toggle_buttons["rain"].collidepoint((mx,my)):
                is_rain = not is_rain
                click_sound.play()
                if is_rain: rain_sound.play(-1)
                else: rain_sound.stop()
            if toggle_buttons["light"].collidepoint((mx,my)):
                headlights_on = not headlights_on
                click_sound.play()
            if game_over and show_retry and retry_button_rect.collidepoint((mx,my)):
                reset_all()
                click_sound.play()
            if success and next_button_rect.collidepoint((mx,my)):
                click_sound.play()
                traffic_sound.stop()
                running = False
                

            if phone_active:
                aw = pygame.Rect(WIDTH//2-130, HEIGHT//2+30, 120, 50)
                dw = pygame.Rect(WIDTH//2+10, HEIGHT//2+30, 120, 50)
                if aw.collidepoint((mx,my)):
                    phone_choice = "answer"
                    phone_active = False
                    game_over = True
                    game_over_msg = "You answered the phone while crossing!"
                    show_retry = True
                    phone_sound.stop()
                    gameover_sound.play()
                if dw.collidepoint((mx,my)):
                    phone_choice = "decline"
                    phone_active = False
                    phone_timer = 0.0
                    phone_sound.stop()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP): move_forward = True
            if event.key in (pygame.K_s, pygame.K_DOWN): move_back = True
            if event.key in (pygame.K_r,) and game_over: reset_all()
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP): move_forward = False
            if event.key in (pygame.K_s, pygame.K_DOWN): move_back = False

    # ---- traffic light ----
    car_state = car_light_state(car_light_timer)
    ped_state = ped_light_state(car_light_timer)

    # ---- green pedestrian timer ----
    if ped_state == "GREEN":
        if not green_timer_running:
            green_timer_running = True
            green_timer = GREEN_TIMER_START
        else:
            green_timer -= dt_seconds
            if green_timer <= 0:
                green_timer = 0
                game_over = True
                game_over_msg = "Time's up during GREEN light!"
                show_retry = True
                gameover_sound.play()
    else:
        green_timer_running = False

    # ---- rain ----
    if is_rain:
        spawn_rain()
        update_rain(dt_seconds)

    # ---- vehicles ----
    for v in vehicles:
        stop_x = STOP_LINE_LEFT - v["w"] - 6 if v["dir"] == 1 else STOP_LINE_RIGHT + 6
        approaching = v["x"] + v["w"] < STOP_LINE_LEFT + 140 if v["dir"]==1 else v["x"] > STOP_LINE_RIGHT - 140
        if car_state == "RED" and approaching:
            v["stopped"] = True
            if v["dir"] == 1 and v["x"] < stop_x: v["x"] += min(v["speed"]*0.3, stop_x-v["x"])
            if v["dir"] == -1 and v["x"] > stop_x: v["x"] -= min(v["speed"]*0.3, v["x"]-stop_x)
        elif car_state == "YELLOW":
            v["stopped"] = False
            v["x"] += v["dir"] * v["speed"] * 0.45 * dt_seconds * 30
        else:
            v["stopped"] = False
            v["x"] += v["dir"] * v["speed"] * dt_seconds * 30
        if v["dir"] == 1 and v["x"] > WIDTH + 300: v["x"] = -300
        if v["dir"] == -1 and v["x"] < -300: v["x"] = WIDTH+300

    # ---- player movement ----
    if not game_over and not success and not phone_active:
        mvy = 0
        if move_forward: mvy -= PLAYER_SPEED * dt_seconds * 60
        if move_back: mvy += PLAYER_SPEED * dt_seconds * 60
        # buttons
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            mx,my = pygame.mouse.get_pos()
            if up_button_rect.collidepoint((mx,my)): mvy -= PLAYER_SPEED * dt_seconds * 60
            if down_button_rect.collidepoint((mx,my)): mvy += PLAYER_SPEED * dt_seconds * 60
        # moving on red -> game over
        if mvy != 0 and ped_state=="RED":
            game_over = True
            game_over_msg = "You moved when pedestrian light was RED!"
            show_retry = True
            gameover_sound.play()
        else:
            player_y += mvy
        player_x = max(8, min(WIDTH-8, player_x))
        player_y = max(8, min(HEIGHT-8, player_y))
        
    # ---- crossing & phone ----
    on_crossing = CROSSING_X <= player_x <= CROSSING_X + CROSSING_W and CROSSING_START_Y <= (player_y + bob_offset) <= CROSSING_END_Y
    if on_crossing and ped_state == "RED" and not game_over:
        game_over = True
        game_over_msg = "You are on the crossing while PEDESTRIAN LIGHT ARE RED!"
        show_retry = True
        gameover_sound.play()

    if on_crossing and not player_entered_crossing:
        player_entered_crossing = True
        crossing_enter_time = time.time()
    if player_entered_crossing and not phone_event_triggered:
        if time.time() - crossing_enter_time >= 0.1:
            phone_active = True
            phone_timer = 0.0
            phone_event_triggered = True
            phone_sound.play(-1)  # loop phone sound until answered/declined
    if phone_active:
        phone_timer += dt_seconds
        if phone_timer > 3.0:
            phone_active = False
            game_over = True
            game_over_msg = "You failed to decline the phone!"
            show_retry = True
            phone_sound.stop()
            gameover_sound.play()

    # success
    if player_y<=FINISH_Y and not game_over:
        success=True
        success_sound.play()

    # bobbing
    if move_forward or move_back:
        bob_offset += bob_dir*0.8
        if bob_offset>6 or bob_offset<-6: bob_dir*=-1
    else:
        bob_offset*=0.7
        bob_offset=0.0 if abs(bob_offset)<0.1 else bob_offset

    # ---- render ----
    window.blit(background,(0,0))
    if is_night and headlights_on:
        for v in vehicles: draw_vehicle_headlight(window,v)
    for v in vehicles: window.blit(v["img"],(int(v["x"]),int(v["y"])))
    window.blit(player_image,(int(player_x),int(player_y+bob_offset)))

    if car_state=="RED": window.blit(red_light,(traffic_x,traffic_y))
    elif car_state=="YELLOW": window.blit(yellow_light,(traffic_x,traffic_y))
    else: window.blit(green_light,(traffic_x,traffic_y))

    # draw hoverable toggles
    draw_hoverable_toggle(window,toggle_buttons["day"],"DAY",not is_night)
    draw_hoverable_toggle(window,toggle_buttons["night"],"NIGHT",is_night)
    draw_hoverable_toggle(window,toggle_buttons["rain"],"RAIN",is_rain)
    draw_hoverable_toggle(window,toggle_buttons["light"],"LIGHT",headlights_on)

    # draw hoverable player buttons
    if not game_over and not success and not phone_active:
        draw_hoverable_button(window, up_button_rect, up_button_img)
        draw_hoverable_button(window, down_button_rect, down_button_img)

    if is_rain:
        draw_rain(window)
        overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((40,40,60,40))
        window.blit(overlay,(0,0))

    if is_night:
        overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((0,0,0,140))
        window.blit(overlay,(0,0))

    car_text = pixel_font_small.render(f'Car Light: {car_state}',True,(255,255,255))
    ped_text = pixel_font_small.render(f'Pedestrian Light: {ped_state}',True,(255,255,255))
    window.blit(car_text,(30,70))
    window.blit(ped_text,(30,94))
    
    if ped_state == "RED":
        window.blit(ped_red_light, (ped_light_x, ped_light_y))
    elif ped_state == "YELLOW":
        window.blit(ped_yellow_light, (ped_light_x, ped_light_y))
    else:
        window.blit(ped_green_light, (ped_light_x, ped_light_y))

    if ped_state == "GREEN":
        timer_text = pixel_font_small.render(f"Time: {int(green_timer)}", True, (255, 255, 255))
        window.blit(timer_text, (WIDTH - 130, 20))

    if phone_active:
        s = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        s.fill((0,0,0,120)); window.blit(s,(0,0))
        info = pixel_font_small.render("Phone is ringing!",True,(255,255,255))
        window.blit(info,info.get_rect(center=(WIDTH//2,HEIGHT//2-20)))
        aw = pygame.Rect(WIDTH//2-130, HEIGHT//2+30,120,50)
        dw = pygame.Rect(WIDTH//2+10, HEIGHT//2+30,120,50)
        pygame.draw.rect(window,(200,30,30),aw,border_radius=6)
        pygame.draw.rect(window,(30,200,30),dw,border_radius=6)
        window.blit(pixel_font_small.render("ANSWER",True,(255,255,255)),pixel_font_small.render("ANSWER",True,(255,255,255)).get_rect(center=aw.center))
        window.blit(pixel_font_small.render("DECLINE",True,(255,255,255)),pixel_font_small.render("DECLINE",True,(255,255,255)).get_rect(center=dw.center))

    if game_over:
        overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((0,0,0,200)); window.blit(overlay,(0,0))
        go = pixel_font_big.render("GAME OVER",True,(255,32,32))
        window.blit(go,go.get_rect(center=(WIDTH//2,HEIGHT//2-80)))
        msg = pixel_font_small.render(game_over_msg,True,(255,255,255))
        window.blit(msg,msg.get_rect(center=(WIDTH//2,HEIGHT//2-20)))
        if show_retry:
            draw_hoverable_button(window, retry_button_rect, retry_button_img)

    if success:
        overlay = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((0,0,0,100)); window.blit(overlay,(0,0))
        win = pixel_font_big.render("SUCCESS!",True,(0,230,40))
        window.blit(win,win.get_rect(center=(WIDTH//2,HEIGHT//2)))
        mx, my = pygame.mouse.get_pos()

        if next_button_rect.collidepoint((mx, my)):
            if not hover_next_played:
                click_sound.play()   # hover sound
                hover_next_played = True
        else:
            hover_next_played = False

        draw_hoverable_button(window, next_button_rect, next_button_img, 1.01)
     
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()