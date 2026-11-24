import pygame
import sys
import os
import math
import random

def show_good_job_screen():
    # ------------------ INIT ------------------
    pygame.init()
    pygame.mixer.init()

    # ------------------ WINDOW ------------------
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Good Job Screen")
    clock = pygame.time.Clock()

    # ------------------ CURRENT FOLDER ------------------
    current_folder = os.path.dirname(os.path.abspath(__file__))

    # ------------------ LOAD FONTS ------------------
    pixel_font = pygame.font.Font(os.path.join(current_folder, "BoldPixels.ttf"), 100)
    pixel_font_small = pygame.font.Font(os.path.join(current_folder, "BoldPixels.ttf"), 33)

    # ------------------ LOAD IMAGES ------------------
    def load_image(filename, scale=None):
        path = os.path.join(current_folder, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        else:
            print(f" FILE NOT FOUND: {filename}")
            return None

    flashcard_bg = load_image("flashcardbackground2.png", (WIDTH, HEIGHT)) 
    textbox_width, textbox_height = 750, 450
    textbox_bg = load_image("yellowtextbox.png", (textbox_width, textbox_height))
    textbox_pos = ((WIDTH - textbox_width)//2, (HEIGHT - textbox_height)//2)

    badge_img = load_image("buttonbadge.png")
    if badge_img:
        badge_img = pygame.transform.scale(badge_img, (150, 150))

    back_btn_rect = pygame.Rect(400, 400, 100, 100)
    back_img = load_image("backmainmenu.png", (back_btn_rect.width, back_btn_rect.height))

    # ------------------ LOAD SOUNDS ------------------
    def load_sound(filename):
        path = os.path.join(current_folder, filename)
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        else:
            print(f" SOUND NOT FOUND: {filename}")
            return None

    typing_sound = load_sound("typewrittersound.wav")
    achievement_sound = load_sound("achievement.wav")
    button_click_sound = load_sound("click.wav")
    badge_sound = load_sound("woosh.wav")

    # Dedicated channels
    typing_channel = pygame.mixer.Channel(1)
    click_channel = pygame.mixer.Channel(2)
    badge_channel = pygame.mixer.Channel(3)
    achievement_channel = pygame.mixer.Channel(4)

    # ------------------ MAIN LOOP ------------------
    running = True

    # Badge initial position
    badge_x = WIDTH//2 - badge_img.get_width()//2 + 200
    badge_y = -badge_img.get_height()
    badge_target_y = 290
    badge_speed = 10

    # Scroll variables for road background
    scroll_x = 0
    scroll_speed = 2 

    # Flags
    title_done = False
    text_done = False
    badge_done = False
    badge_sound_played = False
    back_button_visible = False

    # Info text
    lines = [
        "Congrats! You have completed the quest",
        "in SafeVille!",
        "You have been rewarded the",
        "Road Rangers Badge!",
    ]
    rendered_lines = [""] * len(lines)
    current_line_index = 0
    current_char_index = 0

    # Hover click sound flag
    back_hover_played = False

    # Start achievement sound
    if achievement_sound:
        achievement_channel.play(achievement_sound)

    achievement_start_time = pygame.time.get_ticks()

    while running:
        screen.fill((0,0,0))

        # SCROLLING BACKGROUND
        if flashcard_bg:
            scroll_x -= scroll_speed
            if scroll_x <= -WIDTH:
                scroll_x = 0
            screen.blit(flashcard_bg, (scroll_x, 0))
            screen.blit(flashcard_bg, (scroll_x + WIDTH, 0))
        else:
            screen.fill((240, 240, 240))

        # TEXT BOX
        if textbox_bg:
            screen.blit(textbox_bg, textbox_pos)

        # GLITCH TITLE
        now = pygame.time.get_ticks()
        if now - achievement_start_time < 1500:
            for _ in range(2):
                offset_x = random.randint(-2,2)
                offset_y = random.randint(-2,2)
                color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                title = pixel_font.render("GOOD JOB!", True, color)
                screen.blit(title, (225+offset_x, 110+offset_y))
        else:
            title = pixel_font.render("GOOD JOB!", True, (0,0,0))
            screen.blit(title, (225,110))
            title_done = True

        # TYPEWRITER TEXT
        if title_done and not text_done:
            if current_line_index < len(lines):
                line = lines[current_line_index]
                if current_char_index < len(line):
                    rendered_lines[current_line_index] = line[:current_char_index+1]
                    current_char_index += 1
                    if typing_sound:
                        typing_channel.play(typing_sound)
                else:
                    current_line_index +=1
                    current_char_index = 0
            else:
                text_done = True
                back_button_visible = True
                if typing_channel.get_busy():
                    typing_channel.stop()

        # INFO TEXT
        for i, rline in enumerate(rendered_lines):
            rendered = pixel_font_small.render(rline, True, (0,0,0))
            screen.blit(rendered, (150, 220 + i*40))

        # BADGE ANIMATION
        if text_done:
            if badge_y < badge_target_y:
                badge_y += badge_speed
            else:
                badge_y = badge_target_y
                badge_done = True
                if badge_sound and not badge_sound_played:
                    badge_channel.play(badge_sound)
                    badge_sound_played = True

            glow_surf = pygame.Surface((badge_img.get_width()+20, badge_img.get_height()+20), pygame.SRCALPHA)
            glow_alpha = 80 + 50*math.sin(pygame.time.get_ticks()*0.005)
            pygame.draw.ellipse(glow_surf, (255,255,150,int(glow_alpha)), glow_surf.get_rect())
            screen.blit(glow_surf, (badge_x-10, badge_y-10))
            screen.blit(badge_img, (badge_x, badge_y))

        # HOME BUTTON
        mouse_pos = pygame.mouse.get_pos()
        if back_button_visible:
            mouse_hovering = back_btn_rect.collidepoint(mouse_pos)
            if mouse_hovering:
                scale_img = pygame.transform.scale(back_img, (int(back_img.get_width()*1.1), int(back_img.get_height()*1.1)))
                screen.blit(scale_img, (back_btn_rect.x-5, back_btn_rect.y-5))
                if not back_hover_played and button_click_sound:
                    click_channel.play(button_click_sound)
                    back_hover_played = True
            else:
                screen.blit(back_img, back_btn_rect)
                back_hover_played = False

        # EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn_rect.collidepoint(event.pos):
                    if button_click_sound:
                        click_channel.play(button_click_sound)
                    running = False

        pygame.display.update()
        clock.tick(60)
