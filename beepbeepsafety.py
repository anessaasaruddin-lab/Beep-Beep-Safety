import pygame
import math
from button import Button
from instructionscreen import InstructionScreen
from questboard import QuestBoard
from tutorial_scenecopy import TutorialScene
from flashcard_scene import FlashcardScene
from lesson_scene_1 import LessonScene1
from lesson_scene_2 import LessonScene2
from lesson_scene_3 import LessonScene3
from completion_scene import CompletionScene
from quiz import RoadSafetyQuiz
from simulation_intro_scene import SimulationIntroScene
from simulation_scene import SimulationScene
from good_job_scene import GoodJobScene


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()


pygame.mixer.set_num_channels(8)
ui_channel = pygame.mixer.Channel(7)
voice_channel = pygame.mixer.Channel(6)
flip_channel = pygame.mixer.Channel(5)

# ----------------------------------------
# WINDOW SETTINGS
# ----------------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Beep-Beep Safety")
quest_board = QuestBoard(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

clock = pygame.time.Clock()

bg_music = { "1bg_img.png": "menu_bg.mp3",
             "safeville.png": "safeville_bg.mp3",
             "kid.png": "danger_bg.mp3",
             "car.png": "hero_bg.mp3"
}

current_music = None

next_btn_sound = pygame.mixer.Sound("next_sound.wav")
next_btn_sound.set_volume(1.0)

start_btn_sound = pygame.mixer.Sound("start_sound.mp3")
start_btn_sound.set_volume(1.0)

menu_btn_sound = pygame.mixer.Sound("button2sound.mp3")
menu_btn_sound.set_volume(1.0)

def play_bg_music(bg_name):
    global current_music
    music = bg_music.get(bg_name)

    if music and current_music != music:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(0) #play ONCE only
        current_music = music

story_music = "story_bg.wav"
story_music_playing = False

def play_story_music():
    global story_music_playing
    if not story_music_playing:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(story_music)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)  # loop
        story_music_playing = True

def stop_story_music():
    global story_music_playing
    pygame.mixer.music.stop()
    story_music_playing = False

text_sound = pygame.mixer.Sound("text_blip.wav")
text_sound.set_volume(1.0)


launch_tutorial = False

# ----------------------------------------
# BACKGROUND SETUP
# ----------------------------------------
background_order = ["1bg_img.png", "safeville.png", "kid.png", "car.png"]
scrollable_backgrounds = ["1bg_img.png", "safeville.png", "kid.png"]

backgrounds = {}

for bg_name in background_order:
    try:
        bg = pygame.image.load(bg_name).convert()
        if bg.get_height() != SCREEN_HEIGHT:
            bg = pygame.transform.scale(bg, (bg.get_width(), SCREEN_HEIGHT))
        backgrounds[bg_name] = bg
    except:
        bg = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))

        if "1bg_img" in bg_name:
            color_base = (60, 80, 100)
        elif "safeville" in bg_name:
            color_base = (60, 120, 60)
        elif "kid" in bg_name:
            color_base = (120, 60, 40)
        elif "car" in bg_name:
            color_base = (150, 40, 40)
        else:
            color_base = (100, 40, 120)

        for x in range(0, SCREEN_WIDTH * 2, 40):
            color = (color_base[0] + (x // 10) % 40,
                     color_base[1] + (x // 15) % 40,
                     color_base[2] + (x // 20) % 40)
            pygame.draw.rect(bg, color, (x, 0, 40, SCREEN_HEIGHT))

        backgrounds[bg_name] = bg

current_bg_index = 0
current_bg_name = background_order[current_bg_index]
current_bg = backgrounds[current_bg_name]

scroll = 0
bg_width = current_bg.get_width()
tiles = math.ceil(SCREEN_WIDTH / bg_width) + 1
should_scroll = True

# ----------------------------------------
# LOAD TITLE
# ----------------------------------------
title_img = pygame.image.load("tajuk.png").convert_alpha()
title_img = pygame.transform.scale(title_img, (800, 500))
title_x = SCREEN_WIDTH // 2 - title_img.get_width() // 2
title_y = 40

# ----------------------------------------
# BUTTONS
# ----------------------------------------
def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        return None

def fallback_surface(w, h, col, text=""):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(col)
    pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 3)
    if text:
        f = pygame.font.SysFont("arial", 20)
        ts = f.render(text, True, (255, 255, 255))
        surf.blit(ts, ts.get_rect(center=(w // 2, h // 2)))
    return surf

start_img = load_image("starts_btn.png") or fallback_surface(200, 120, (0, 150, 0), "START")
tutorial_img = load_image("tutorial_btn.png") or fallback_surface(90, 90, (200, 180, 0), "HELP")
quit_img = load_image("quit_btn.png") or fallback_surface(100, 60, (180, 0, 0), "QUIT")
next_img = load_image("next_btn.png") or fallback_surface(80, 40, (0, 100, 200), "NEXT")

start_scale = 0.8
start_w = int(start_img.get_width() * start_scale)
start_h = int(start_img.get_height() * start_scale)

start_x = SCREEN_WIDTH // 2 - start_w // 2
start_y = SCREEN_HEIGHT // 2 - start_h // 2 + 200

start_button = Button(start_x, start_y, start_img, start_scale)

tutorial_button = Button(SCREEN_WIDTH - int(tutorial_img.get_width()*0.4) - 20,
                         SCREEN_HEIGHT - int(tutorial_img.get_height()*0.4) - 20,
                         tutorial_img, 0.4)

quit_button = Button(20, 20, quit_img, 0.4)

next_button = Button(SCREEN_WIDTH - int(next_img.get_width()*0.3) - 20,
                     SCREEN_HEIGHT - int(next_img.get_height()*0.3) - 20,
                     next_img, 0.3)

# ----------------------------------------
# INSTRUCTIONS
# ----------------------------------------
instruction_screen = InstructionScreen(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

# ----------------------------------------
# STORY TEXT
# ----------------------------------------
story_text = {
    "safeville.png": "Welcome to Safeville...\nA peaceful town where your journey begins and\nevery adventure begins with a single, safe step.",
    "kid.png": "But oh no!\nThe traffic light is broken and the kids are crossing\nthe road carelessly, how dangerous.",
    "car.png": "You have been chosen as the town hero!\nhelp us to save the world!."
}

try:
    pixel_font = pygame.font.Font("pixel_font.otf", 32)
except:
    pixel_font = pygame.font.SysFont("arial", 32)

animated_text = ""
full_text = ""
text_index = 0
text_speed = 4
text_cooldown = 0

def reset_animated_text():
    global animated_text, full_text, text_index, text_cooldown
    full_text = story_text.get(current_bg_name, "")
    animated_text = ""
    text_index = 0
    text_cooldown = 0

def draw_animated_story():
    global animated_text, full_text, text_index, text_cooldown
    if not full_text:
        return

    if text_index < len(full_text):
        text_cooldown += 1
        if text_cooldown >= text_speed:
            char = full_text[text_index]
            animated_text += char
            text_index += 1
            text_cooldown = 0

            if char not in ["", "\n"]:
                text_sound.play()

    y = SCREEN_HEIGHT - 140
    for line in animated_text.split("\n"):
        shadow = pixel_font.render(line, True, (0, 0, 0))
        text_surface = pixel_font.render(line, True, (255, 255, 255))
        screen.blit(shadow, (43, y + 3))
        screen.blit(text_surface, (40, y))
        y += 40

# ----------------------------------------
# BACKGROUND DRAWING
# ----------------------------------------
def draw_scrolling_background():
    global current_bg, bg_width, tiles, scroll

    background = backgrounds[current_bg_name]

    if background != current_bg:
        current_bg = background
        bg_width = current_bg.get_width()
        tiles = math.ceil(SCREEN_WIDTH / bg_width) + 1
        scroll = 0

    if current_bg_name == "car.png":
        rect = current_bg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(current_bg, rect)
        return

    for i in range(tiles):
        screen.blit(current_bg, (i * bg_width + scroll, 0))

    if should_scroll and current_bg_name in scrollable_backgrounds:
        scroll -= 1
        if abs(scroll) > bg_width:
            scroll = 0

# ----------------------------------------
# STATE MACHINE
# ----------------------------------------
MENU = 0
PLAYING = 1
INSTRUCTIONS = 2
TUTORIAl = 3
QUIZ = 4
current_state = MENU

def start_game():
    global current_bg_index, current_bg_name
    current_bg_index = 1
    current_bg_name = background_order[current_bg_index]
    reset_animated_text()

def next_background():
    global current_bg_index, current_bg_name
    if current_bg_index < len(background_order) - 1:
        current_bg_index += 1
    current_bg_name = background_order[current_bg_index]
    reset_animated_text()

def stop_all_music():
    global current_music
    pygame.mixer.music.stop()
    current_music = None


# ----------------------------------------
# MAIN LOOP
# ----------------------------------------
run = True
while run:

    clock.tick(60)
    draw_scrolling_background()
    play_bg_music(current_bg_name)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if current_state in (PLAYING, INSTRUCTIONS):
                current_state = MENU
                current_bg_index = 0
                current_bg_name = background_order[0]

        if current_state == INSTRUCTIONS:
            instruction_screen.update_scroll(event)

    # --------------------
    # MENU
    # --------------------
    if current_state == MENU:
        screen.blit(title_img, (title_x, title_y))

        if start_button.draw(screen):
            ui_channel.play(start_btn_sound)
            start_game()
            current_state = PLAYING

        if tutorial_button.draw(screen):
            ui_channel.play(menu_btn_sound)
            current_state = INSTRUCTIONS

        if quit_button.draw(screen):
            ui_channel.play(menu_btn_sound)
            pygame.time.delay(150)
            run = False

    # --------------------
    # PLAYING
    # --------------------
    elif current_state == PLAYING:

        if quest_board.visible:
            result = quest_board.draw()

            if result == "accept":
                ui_channel.play(menu_btn_sound)
                quest_board.close()

                screen.fill((0, 0, 0))
                pygame.display.flip()

                #stop all music before tutorial scene
                stop_all_music()

                #start story music once
                play_story_music()

                #scene 1
                tutorial_scene = TutorialScene(screen, voice_channel)
                tutorial_scene.run()

                completed = {1:False, 2:False, 3:False}

                while True:

                    #scene 2
                    flash_scene = FlashcardScene(screen, flip_channel)
                    flash_scene.run()

                    #lesson scenes
                    if flash_scene.next_scene == "lesson1":
                        LessonScene1(screen, voice_channel).run()
                        completed[1] = True

                    elif flash_scene.next_scene == "lesson2":
                        LessonScene2(screen, voice_channel).run()
                        completed[2] = True
                    
                    elif flash_scene.next_scene == "lesson3":
                        LessonScene3(screen, voice_channel).run()
                        completed[3] = True

                    #completion scene
                    if all(completed.values()):
                        CompletionScene(screen).run()
                        stop_story_music()

                        break
                stop_all_music()   

                #quiz scene
                quiz = RoadSafetyQuiz(screen)
                quiz.run()

                #simulation intro
                SimulationIntroScene(screen).run()

                #run simulation
                scene = SimulationScene(screen)
                result = scene.run()

                good_job_scene = GoodJobScene(screen)
                good_job_scene.run()
                

                current_state = MENU
                current_bg_index = 0
                current_bg_name = background_order[0]


            elif result == "continue":
                  quest_board.close()
                  game_state = "MENU"

        else:
            # Normal gameplay
            if next_button.draw(screen):
                print("next clicked")
                ui_channel.play(next_btn_sound)

                # Save previous bg
                previous_bg = current_bg_name

                # Move to next bg
                next_background()

                # Only open quest board if clicking NEXT while on car.png
                if previous_bg == "car.png":
                    quest_board.open()

            draw_animated_story()
        
    # --------------------
    # INSTRUCTIONS
    # --------------------
    elif current_state == INSTRUCTIONS:
        instruction_screen.draw()
    pygame.display.flip()
pygame.quit()