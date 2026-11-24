import pygame
import sys

pygame.init()
pygame.mixer.init()  # Initialize mixer for sounds

# Window
SCREEN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("Road Safety Quiz")

# Font
FONT = pygame.font.SysFont("ByteBounce", 46)
BIG_FONT = pygame.font.SysFont("ByteBounce", 46)

# Load sounds
click_sound = pygame.mixer.Sound("clicks.mp3")       # button click
success_sound = pygame.mixer.Sound("success.mp3")   # result screen

# Quiz Data (correct answers fixed)
questions = [
    {
        "q": "What should you do at red light?",
        "options": ["Go faster", "Stop and wait", "Turn around", "Follow cars"],
        "answer": 1  # B -> index 1
    },
    {
        "q": "Where should you cross the road?",
        "options": ["Anywhere", "At zebra crossing", "In the middle of traffic", "Behind car"],
        "answer": 1
    },
    {
        "q": "Is it okay to text while walking across the road?",
        "options": ["Yes", "No"],
        "answer": 1
    }
]

current_question = 0
score = 0
selected = None
state = "quiz"  # Add state to manage screens

def draw_text(text, x, y, font=FONT, color=(255, 255, 255)):
    render = font.render(text, True, color)
    SCREEN.blit(render, (x, y))

def quiz_screen(events):
    global current_question, score, selected, state

    SCREEN.fill((15, 15, 55))
    q = questions[current_question]

    # Question
    draw_text(f"Question {current_question + 1}/{len(questions)}", 50, 30, FONT)
    draw_text(q["q"], 50, 100, BIG_FONT)

    mouse = pygame.mouse.get_pos()
    option_y = 200

    # Draw answer boxes
    for i, option in enumerate(q["options"]):
        rect = pygame.Rect(50, option_y, 700, 60)

        if rect.collidepoint(mouse):
            pygame.draw.rect(SCREEN, (80, 80, 200), rect)
        elif selected == i:
            pygame.draw.rect(SCREEN, (120, 120, 250), rect)
        else:
            pygame.draw.rect(SCREEN, (40, 40, 120), rect)

        draw_text(option, 65, option_y + 15)
        option_y += 90

    # NEXT button
    # NEXT button
    next_btn = pygame.Rect(763, 500, 120, 50)

    # Button disabled until user chooses an answer
    if selected is not None:
      pygame.draw.rect(SCREEN, (200, 180, 60), next_btn)
      draw_text("NEXT", 784, 508)
    else:
      pygame.draw.rect(SCREEN, (120, 120, 120), next_btn)
      draw_text("NEXT", 784, 508)


    # Handle events
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check option clicks
            option_y = 200
            for i in range(len(q["options"])):
                rect = pygame.Rect(50, option_y, 700, 60)
                if rect.collidepoint(mouse):
                    selected = i
                    click_sound.play()  # <-- play click on option selection
                option_y += 90

            # Check NEXT
            if selected is not None and next_btn.collidepoint(mouse):
                click_sound.play()  # <-- play click on NEXT button
                if selected == q["answer"]:
                    score += 1
                selected = None
                current_question += 1
                if current_question >= len(questions):
                    state = "result"

def result_screen(events):
    global current_question, score, selected, state

    # Play success sound once
    if not hasattr(result_screen, "played_sound"):
        success_sound.play()
        result_screen.played_sound = True

    # Draw background
    try:
        result_image = pygame.image.load("backgroundscore2.jpg")
        result_image = pygame.transform.scale(result_image, (900, 600))
        SCREEN.blit(result_image, (0, 0))
    except pygame.error:
        SCREEN.fill((135, 206, 235))
        
    # Centered Board
    try:
        board = pygame.image.load("boardscore3.jpg")
        board = pygame.transform.scale(board, (717, 367))
        board_x = 87
        board_y = 80
        SCREEN.blit(board, (board_x, board_y))
    except:
        pygame.draw.rect(SCREEN, (200, 180, 140), (200, 150, 500, 260))

    # Score and rank
    score_text = FONT.render(f"Score: {score}/{len(questions)}", True, (0, 0, 0))
    SCREEN.blit(score_text, (board_x + 270, board_y + 148))

    if score == len(questions):
        rank = "Rank: Superior"
    elif score == len(questions) - 1:
        rank = "Rank: Master"
    elif score >= len(questions) // 2:
        rank = "Rank: Elite"
    else:
        rank = "Rank: Rookie"

    rank_text = FONT.render(rank, True, (0, 0, 0))
    SCREEN.blit(rank_text, (board_x + 270, board_y + 245))

    # Buttons
    mouse = pygame.mouse.get_pos()
    retry_btn = pygame.Rect(50, 500, 120, 50)
    next_btn = pygame.Rect(750, 500, 120, 50)

    try:
        retry_image = pygame.image.load("retry.png")
        retry_image = pygame.transform.scale(retry_image, (150, 60))
        SCREEN.blit(retry_image, (70, 500))
    except pygame.error:
        pygame.draw.rect(SCREEN, (0, 255, 0), retry_btn)
        draw_text("RETRY", 65, 515, FONT, (0, 0, 0))

    try:
        next_image = pygame.image.load("next1.png").convert_alpha()
        orig_w, orig_h = next_image.get_size()
        scale_factor = 0.3
        next_image = pygame.transform.scale(next_image, (int(orig_w * scale_factor), int(orig_h * scale_factor)))
        SCREEN.blit(next_image, (730, 490))
    except pygame.error:
        pygame.draw.rect(SCREEN, (0, 0, 255), next_btn)
        draw_text("NEXT", 765, 515, FONT, (255, 255, 255))

    # Handle button events
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if retry_btn.collidepoint(mouse):
                click_sound.play()  # <-- click on retry
                current_question = 0
                score = 0
                selected = None
                state = "quiz"
                # Reset success sound flag
                if hasattr(result_screen, "played_sound"):
                    del result_screen.played_sound
            if next_btn.collidepoint(mouse):
                click_sound.play()  # <-- click on next
                pygame.quit()
                sys.exit()

# MAIN LOOP
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if state == "quiz":
        quiz_screen(events)
    elif state == "result":
        result_screen(events)

    pygame.display.update()

pygame.quit()
sys.exit()
