import pygame
import sys

pygame.init()

# Window setup
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beep Beep Safety")

clock = pygame.time.Clock()
FPS = 10

# ==================================================
# LOAD IMAGES
# ==================================================
background = pygame.image.load("bgdilah.png").convert()
sprite_sheet = pygame.image.load("speak2.png").convert_alpha()   # NPC animation
dialog_box = pygame.image.load("dialog.png").convert_alpha()
next_img = pygame.image.load("next.png").convert_alpha()
card_bg = pygame.image.load("cardbackground.png").convert()
takequiz_btn = pygame.image.load("takequiz.png").convert_alpha()

# Flashcard fronts (scene 2)
card1 = pygame.image.load("card1.png").convert_alpha()
card2 = pygame.image.load("card2.png").convert_alpha()
card3 = pygame.image.load("card3.png").convert_alpha()

# Flashcard backs (lessons)
flash_back_1 = pygame.image.load("flashcard1.png").convert_alpha()
flash_back_2 = pygame.image.load("flashcard2.png").convert_alpha()
flash_back_3 = pygame.image.load("flashcard3.png").convert_alpha()

# Lesson background
lesson_bg = pygame.image.load("flashcardbackground2.png").convert()

# Resize some assets
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Dialog box sizing (used in scene1 & lessons)
dialog_box_width = 750
dialog_box_height = 310
dialog_img = pygame.transform.scale(dialog_box, (dialog_box_width, dialog_box_height))
dialog_x = (WIDTH - dialog_box_width) // 2
dialog_y = HEIGHT - dialog_box_height - 30
dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_box_width, dialog_box_height)

# Sprite sheet
scale_factor = 1.0
sprite_sheet = pygame.transform.rotozoom(sprite_sheet, 0, scale_factor)

FRAME_WIDTH = sprite_sheet.get_width() // 4
FRAME_HEIGHT = sprite_sheet.get_height()

frames = []
for i in range(4):
    frame = sprite_sheet.subsurface((i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
    frames.append(frame)

current_frame = 0
frame_timer = 0

# Next button (we will scale when drawing)
NEXT_BTN_SIZE = (70, 70)

# ==================================================
# NPC sprite sheet -> frames
# ==================================================
scale_factor = 0.8
sprite_sheet = pygame.transform.rotozoom(sprite_sheet, 0, scale_factor)
FRAME_WIDTH = sprite_sheet.get_width() // 4
FRAME_HEIGHT = sprite_sheet.get_height()
frames = [sprite_sheet.subsurface((i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)) for i in range(4)]
current_frame = 0
frame_timer = 0
FRAME_DELAY = 6

# ==================================================
# Fonts
# ==================================================
dialog_font = pygame.font.Font("pixel_font.otf", 28)
title_font = pygame.font.Font("pixel_font.otf", 40)

# ==================================================
# Scene & state
# ==================================================
scene = 1  # 1 = dialog intro, 2 = flashcard menu, 10/11/12 = lessons, 13 = completed
# viewed flags
viewed_1 = False
viewed_2 = False
viewed_3 = False

# Dialog intro text
intro_text = "Hi! I'm Officer Lina. Before you head outside, let's learn some important safety tips to keep you protected and aware."
typing_index = 0
typing_speed = 2  # characters per update tick
displayed_text = ""
show_next_button = False
dialog_scale = 1.0  # keep full scale for simplicity in this version

# ==================================================
# Flashcards (scene 2) sizing & positions
# ==================================================
card_w, card_h = 200, 260
card1_thumb = pygame.transform.scale(card1, (card_w, card_h))
card2_thumb = pygame.transform.scale(card2, (card_w, card_h))
card3_thumb = pygame.transform.scale(card3, (card_w, card_h))

card1_rect = card1_thumb.get_rect(center=(WIDTH//2 - 250, HEIGHT//2 - 20))
card2_rect = card2_thumb.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
card3_rect = card3_thumb.get_rect(center=(WIDTH//2 + 250, HEIGHT//2 - 20))

hover_scale = 1.08

# Flip animation state
flipping = False
flip_angle = 0
selected_card = None

# Star reward animation (scene 13)
stars = []
star_timer = 0
STAR_COUNT = 12

# Helper: wrap text into lines
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for w in words:
        test = current + w + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current.strip())
            current = w + " "
    if current.strip():
        lines.append(current.strip())
    return lines

# Helper: draw text (simple)
def draw_text_lines(text, font, color, surface, x, y, max_width):
    lines = wrap_text(text, font, max_width)
    yy = y
    for line in lines:
        surf = font.render(line, True, color)
        surface.blit(surf, (x, yy))
        yy += font.get_linesize()
    return yy

# Create star positions (centered)
def init_stars():
    stars.clear()
    for i in range(STAR_COUNT):
        angle = i * (360 / STAR_COUNT)
        radius = 10 + i * 3
        stars.append({
            "x": WIDTH//2 + (i - STAR_COUNT/2) * 12,
            "y": HEIGHT//2 - 60,
            "r": 2 + (i % 4),
            "speed": 0.02 + (i % 3) * 0.01,
            "phase": i * 10
        })

init_stars()

# Main loop
while True:
    clicked = False
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True

        # Scene-specific click handling (we mostly check in-event)
        if scene == 1 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # check next button area (we compute it below)
            pass

        if scene == 2 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if card1_rect.collidepoint(event.pos):
                flipping = True
                selected_card = 1
                flip_angle = 0
            elif card2_rect.collidepoint(event.pos):
                flipping = True
                selected_card = 2
                flip_angle = 0
            elif card3_rect.collidepoint(event.pos):
                flipping = True
                selected_card = 3
                flip_angle = 0

    # ---------------------------
    # NPC frame update
    # ---------------------------
    frame_timer += 1
    if frame_timer >= FRAME_DELAY:
        current_frame = (current_frame + 1) % len(frames)
        frame_timer = 0

    # ---------------------------
    # SCENE 1: Intro dialog with typing effect
    # ---------------------------
    
    if scene == 1:

        screen.blit(background, (0, 0))

        # typing effect
        if typing_index < len(intro_text):
            typing_index += typing_speed
            displayed_text = intro_text[:typing_index]
            show_next_button = False
        else:
            displayed_text = intro_text
            show_next_button = True

        # ========= SPRITE (NPC) =========
        npc_surf = frames[current_frame]
        npc_scaled = pygame.transform.rotozoom(npc_surf, 0, 1.0)   # scale 0.8
        npc_draw_pos = (70, 280)                                   # x=70, y=280
        screen.blit(npc_scaled, npc_draw_pos)

        # ========= DIALOG BOX =========
        dialog_width = 750
        dialog_height = 310
        dialog_x = 150
        dialog_y = 50

        dialog_img_resized = pygame.transform.scale(dialog_box, (dialog_width, dialog_height))
        screen.blit(dialog_img_resized, (dialog_x, dialog_y))

        # ========= TYPED TEXT =========
        text_x = 300
        text_y = 150
        text_width = 500

        draw_text_lines(displayed_text, dialog_font, (0, 0, 0),
                        screen, text_x, text_y, text_width)

        # ========= NEXT BUTTON =========
        if show_next_button:
            scaled_next = pygame.transform.scale(next_img, NEXT_BTN_SIZE)
            next_rect = scaled_next.get_rect(topleft=(700, 420))   # position requested
            screen.blit(scaled_next, next_rect)

            if clicked and next_rect.collidepoint(mouse_pos):
                scene = 2


    # ---------------------------
    # SCENE 2: Flashcard selection
    # ---------------------------
    elif scene == 2:

        screen.blit(card_bg, (0, 0))
        # draw instruction
        title = title_font.render("CHOOSE A CARD", True, (10,10,10))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

        # draw flashcard thumbnails with hover bounce
        def draw_hover_thumb(img_thumb, rect):
            if rect.collidepoint(mouse_pos):
                scaled = pygame.transform.scale(img_thumb, (int(card_w*hover_scale), int(card_h*hover_scale)))
                new_rect = scaled.get_rect(center=rect.center)
                screen.blit(scaled, new_rect)
            else:
                screen.blit(img_thumb, rect)

        draw_hover_thumb(card1_thumb, card1_rect)
        draw_hover_thumb(card2_thumb, card2_rect)
        draw_hover_thumb(card3_thumb, card3_rect)

        # instruction text
        flip_font = pygame.font.Font("pixel_font.otf", 40)
        flip_text = flip_font.render("TAP TO FLIP", True, (10,10,10))
        screen.blit(flip_text, (WIDTH//2 - flip_text.get_width()//2, HEIGHT - 120))

        # Flip animation handling (if active)
        if flipping:
            flip_angle += 10
            # shrinking then expanding
            if flip_angle <= 90:
                scale = max(1 - (flip_angle / 90), 0.05)
                showing_front = True
            else:
                scale = (flip_angle - 90) / 90
                showing_front = False
            scale = max(scale, 0.05)

            if selected_card == 1:
                front_img = card1_thumb
                back_img = pygame.transform.scale(flash_back_1, (card_w, card_h))
                rect = card1_rect
            elif selected_card == 2:
                front_img = card2_thumb
                back_img = pygame.transform.scale(flash_back_2, (card_w, card_h))
                rect = card2_rect
            else:
                front_img = card3_thumb
                back_img = pygame.transform.scale(flash_back_3, (card_w, card_h))
                rect = card3_rect

            img = front_img if showing_front else back_img
            new_w = max(1, int(card_w * scale))
            flipped = pygame.transform.scale(img, (new_w, card_h))
            flip_rect = flipped.get_rect(center=rect.center)

            # re-draw background/menu and show flipped card
            screen.blit(card_bg, (0, 0))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
            draw_hover_thumb(card1_thumb, card1_rect)
            draw_hover_thumb(card2_thumb, card2_rect)
            draw_hover_thumb(card3_thumb, card3_rect)
            screen.blit(flipped, flip_rect)

            if flip_angle >= 180:
                flipping = False
                flip_angle = 0
                # mark viewed and go to lesson scene
                if selected_card == 1:
                    viewed_1 = True
                    scene = 10
                elif selected_card == 2:
                    viewed_2 = True
                    scene = 11
                else:
                    viewed_3 = True
                    scene = 12

    # ---------------------------
    # SCENE 10 — Lesson for card 1 (flash_back_1 on top)
    # ---------------------------
    elif scene == 10:
        
        # Lesson Background
        lesson_bg = pygame.image.load("flashcardbackground2.png").convert()
        lesson_bg = pygame.transform.scale(lesson_bg, (WIDTH, HEIGHT))
        screen.blit(lesson_bg, (0, 0))

        # NPC (left)
        npc = frames[current_frame]
        npc_pos = (40, 270)
        screen.blit(npc, npc_pos)

        # flashcard back (top center-right area): positioned above dialog box
        card_back = pygame.transform.scale(flash_back_1, (485, 278))
        card_back_rect = card_back.get_rect(center=(WIDTH//2 + 105, dialog_rect.y - 65))
        screen.blit(card_back, card_back_rect)

        # dialog box (bottom)
        dialog_scaled = pygame.transform.scale(dialog_box, (750, 310))
        screen.blit(dialog_scaled, (175, 330))
    
        # text inside dialog
        lesson_text = "Always stop at red, even if no cars are coming!"
        lines = wrap_text(lesson_text, dialog_font, 450)

        y = 430
        for line in lines:
            screen.blit(
                dialog_font.render(line, True, (0, 0, 0)),
                (320, y)   # SAME AS BEFORE
            )
            y += 32

        # next button (bottom-right)
        scaled_next = pygame.transform.scale(next_img, (70, 70))
        next_rect = scaled_next.get_rect(topleft=(750, 475))
        screen.blit(scaled_next, next_rect)

        if clicked and next_rect.collidepoint(mouse_pos):
            # already marked viewed when flipped earlier; just go back to menu or to scene13 if all done
            if viewed_1 and viewed_2 and viewed_3:
                scene = 13
            else:
                scene = 2

    # ---------------------------
    # SCENE 11 — Lesson for card 2
    # ---------------------------
    elif scene == 11:

        lb = pygame.transform.scale(lesson_bg, (WIDTH, HEIGHT))
        screen.blit(lb, (0,0))

        npc = frames[current_frame]
        screen.blit(npc, (40, 270))

        card_back = pygame.transform.scale(flash_back_2, (485, 278))
        card_back_rect = card_back.get_rect(center=(WIDTH//2 + 105, dialog_rect.y - 65))
        screen.blit(card_back, card_back_rect)

        dialog_scaled = pygame.transform.scale(dialog_box, (750, 310))
        screen.blit(dialog_scaled, (175, 330))

        lesson_text = "Always look left and right before stepping forward."
        lines = wrap_text(lesson_text, dialog_font, 450)

        y = 430
        for line in lines:
            screen.blit(
                dialog_font.render(line, True, (0, 0, 0)),
                (320, y)   # SAME AS BEFORE
            )
            y += 32

        scaled_next = pygame.transform.scale(next_img, (70, 70))
        next_rect = scaled_next.get_rect(topleft=(750, 475))
        screen.blit(scaled_next, next_rect)

        if clicked and next_rect.collidepoint(mouse_pos):
            if viewed_1 and viewed_2 and viewed_3:
                scene = 13
            else:
                scene = 2

    # ---------------------------
    # SCENE 12 — Lesson for card 3
    # ---------------------------
    elif scene == 12:

        lb = pygame.transform.scale(lesson_bg, (WIDTH, HEIGHT))
        screen.blit(lb, (0,0))

        npc = frames[current_frame]
        screen.blit(npc, (40, 270))

        card_back = pygame.transform.scale(flash_back_3, (485, 278))
        card_back_rect = card_back.get_rect(center=(WIDTH//2 + 105, dialog_rect.y - 65))
        screen.blit(card_back, card_back_rect)

        dialog_scaled = pygame.transform.scale(dialog_box, (750, 310))
        screen.blit(dialog_scaled, (175, 330))

        lesson_text = "Keep your eyes on the road and not on the phone!"
        lines = wrap_text(lesson_text, dialog_font, 450)

        y = 430
        for line in lines:
            screen.blit(
                dialog_font.render(line, True, (0, 0, 0)),
                (320, y)   # SAME AS BEFORE
            )
            y += 32

        scaled_next = pygame.transform.scale(next_img, (70, 70))
        next_rect = scaled_next.get_rect(topleft=(750, 475))
        screen.blit(scaled_next, next_rect)

        if clicked and next_rect.collidepoint(mouse_pos):
            if viewed_1 and viewed_2 and viewed_3:
                scene = 13
            else:
                scene = 2

    # ---------------------------
    # SCENE 13 — Completed all cards (star reward)
    # ---------------------------
    elif scene == 13:

        # ========= BACKGROUND =========
        screen.blit(background, (0, 0))

        # ========= NPC =========
        npc_surf = frames[current_frame]
        npc_scaled = pygame.transform.rotozoom(npc_surf, 0, 1.0)
        npc_draw_pos = (70, 280)
        screen.blit(npc_scaled, npc_draw_pos)

        # ========= DIALOG BOX =========
        dialog_width = 750
        dialog_height = 310
        dialog_x = 150
        dialog_y = 50

        dialog_img_resized = pygame.transform.scale(dialog_box, (dialog_width, dialog_height))
        screen.blit(dialog_img_resized, (dialog_x, dialog_y))

        # ========= TEXT =========
        final_text = (
        "Great job! You viewed all safety flashcards! "
        "Now let's see what you've learned."
        )

        text_x = 300
        text_y = 150
        text_width = 500

        draw_text_lines(
            final_text,
            dialog_font,
            (0, 0, 0),
            screen,
            text_x,
            text_y,
            text_width
        )

        # ========= TAKE QUIZ BUTTON =========
        quiz_btn_scaled = pygame.transform.scale(takequiz_btn, (200, 150))
        quiz_rect = quiz_btn_scaled.get_rect(topleft=(625, 380))
        screen.blit(quiz_btn_scaled, quiz_rect)

        if clicked and quiz_rect.collidepoint(mouse_pos):
            print("Go to quiz scene")
            # scene = 20  # future quiz scene

            # ========= BACKGROUND =========
            lesson_bg = pygame.image.load("flashcardbackground2.png").convert()
            lesson_bg = pygame.transform.scale(lesson_bg, (WIDTH, HEIGHT))
            screen.blit(lesson_bg, (0, 0))

            # ========= NPC ANIMATION =========
            frame_timer += 1
            if frame_timer >= 10:
                current_frame = (current_frame + 1) % len(frames)
                frame_timer = 0

            screen.blit(frames[current_frame], (50, 330))

            # ========= DIALOG BOX =========
            dialog_scaled = pygame.transform.scale(dialog_box, (750, 310))
            screen.blit(dialog_scaled, (175, 330))

            # ========= TEXT =========
            lesson_text = "Great job! You viewed all safety flashcards! Now let's see what you've learned."
            lines = wrap_text(lesson_text, dialog_font, 450)

            y = 430
            for line in lines:
                screen.blit(
                    dialog_font.render(line, True, (0, 0, 0)),
                    (320, y)
                )
                y += 32

            # ========= TAKE QUIZ BUTTON =========
            quiz_btn_scaled = pygame.transform.scale(takequiz_btn, (150, 70))
            quiz_rect = quiz_btn_scaled.get_rect(topleft=(720, 475))
            screen.blit(quiz_btn_scaled, quiz_rect)

            if clicked and quiz_rect.collidepoint(mouse_pos):
                print("Go to quiz scene!")  # replace later with scene = 20 or quiz logic

    pygame.display.update()
    clock.tick(FPS)
