import pygame
import sys

class RoadSafetyQuiz:
    def __init__(self, screen):
        self.SCREEN = screen
        self.WIDTH, self.HEIGHT = screen.get_size()

        # Fonts
        self.FONT = pygame.font.Font("pixel_font.otf", 32)
        self.BIG_FONT = pygame.font.Font("pixel_font.otf", 46)

        # Sounds
        self.click_sound = pygame.mixer.Sound("clicks.mp3")
        self.success_sound = pygame.mixer.Sound("success.mp3")

        # Music
        self.quiz_music = "quiz_bg.wav"
        self.current_music = None

        # Quiz Data
        self.questions = [
            {
                "q": "What should you do at red light?",
                "options": ["Go faster", "Stop and wait", "Turn around", "Follow cars"],
                "answer": 1
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

        # State
        self.current_question = 0
        self.score = 0
        self.selected = None
        self.state = "quiz"
        self.running = False
        self.played_sound = False

        # Backgrounds
        self.quiz_bg = self.load_image("backgroundquiz.jpg")
        self.result_bg = self.load_image("bgdilah.png")
        self.board = self.load_image("boardscore3.jpg", (717, 367))

        # Buttons
        self.retry_img = pygame.image.load("retry.png").convert_alpha()
        self.next_img = pygame.image.load("next.png").convert_alpha()

        self.retry_base = (140, 70)
        self.retry_hover = (165, 82)

        self.next_base = (85, 85)
        self.next_hover = (100, 100)

    # ---------------- MUSIC ----------------
    def play_music(self, music_file):
        if self.current_music != music_file:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
            self.current_music = music_file

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None

    def load_image(self, path, size=None):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            else:
                img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
            return img
        except:
            return None

    def draw_text(self, text, x, y, font=None, color=(255, 255, 255)):
        if font is None:
            font = self.FONT
        render = font.render(text, False, color)
        self.SCREEN.blit(render, (x, y))

    # ---------------- QUIZ SCREEN ----------------
    def quiz_screen(self, events):
        self.play_music(self.quiz_music)

        if self.quiz_bg:
            self.SCREEN.blit(self.quiz_bg, (0, 0))
        else:
            self.SCREEN.fill((15, 15, 55))
            
        q = self.questions[self.current_question]

        self.draw_text(
            f"Question {self.current_question + 1}/{len(self.questions)}",
            50, 30
        )
        self.draw_text(q["q"], 50, 100, self.BIG_FONT)

        mouse = pygame.mouse.get_pos()
        option_y = 200

        for i, option in enumerate(q["options"]):
            rect = pygame.Rect(50, option_y, 700, 60)

            if rect.collidepoint(mouse):
                pygame.draw.rect(self.SCREEN, (80, 80, 200), rect)
            elif self.selected == i:
                pygame.draw.rect(self.SCREEN, (120, 120, 250), rect)
            else:
                pygame.draw.rect(self.SCREEN, (40, 40, 120), rect)

            self.draw_text(option, 65, option_y + 15)
            option_y += 90

        next_btn = pygame.Rect(763, 500, 120, 50)
        pygame.draw.rect(
            self.SCREEN,
            (200, 180, 60) if self.selected is not None else (120, 120, 120),
            next_btn
        )
        self.draw_text("NEXT", 784, 508)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                option_y = 200
                for i in range(len(q["options"])):
                    rect = pygame.Rect(50, option_y, 700, 60)
                    if rect.collidepoint(mouse):
                        self.selected = i
                        self.click_sound.play()
                    option_y += 90

                if self.selected is not None and next_btn.collidepoint(mouse):
                    self.click_sound.play()
                    if self.selected == q["answer"]:
                        self.score += 1
                    self.selected = None
                    self.current_question += 1
                    if self.current_question >= len(self.questions):
                        self.state = "result"
                        self.played_sound = False

    # ---------------- RESULT SCREEN ----------------
    def result_screen(self, events):

        if not self.played_sound:
            self.success_sound.play()
            self.played_sound = True

        self.SCREEN.blit(self.result_bg, (0, 0))

        board_x, board_y = 87, 80
        self.SCREEN.blit(self.board, (board_x, board_y))

        self.draw_text(
            f"Score: {self.score}/{len(self.questions)}",
            board_x + 270, board_y + 150,
            color=(0, 0, 0)
        )

        # -------- RANK --------
        if self.score == 3:
            rank = "Rank: Superior"
        elif self.score == 2:
            rank = "Rank: Elite"
        else:
            rank = "Rank: Rookie"

        self.draw_text(rank, board_x + 260, board_y + 230, color=(0, 0, 0))

        mouse = pygame.mouse.get_pos()
        center_x = self.WIDTH // 2

        # -------- FAIL → RETRY --------
        if self.score < len(self.questions):
            base_rect = pygame.Rect(
                center_x - self.retry_base[0] // 2, 500, *self.retry_base
            )

            if base_rect.collidepoint(mouse):
                img = pygame.transform.scale(self.retry_img, self.retry_hover)
                rect = img.get_rect(center=base_rect.center)
            else:
                img = pygame.transform.scale(self.retry_img, self.retry_base)
                rect = img.get_rect(topleft=base_rect.topleft)

            self.SCREEN.blit(img, rect)

            self.draw_text(
                "You must score 3/3 to continue!",
                board_x + 190, board_y + 300,
                color=(200, 0, 0)
            )

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rect.collidepoint(mouse):
                        self.click_sound.play()
                        self.reset()

        # -------- SUCCESS → NEXT --------
        else:
            base_rect = pygame.Rect(
                center_x - self.next_base[0] // 2, 500, *self.next_base
            )

            if base_rect.collidepoint(mouse):
                img = pygame.transform.scale(self.next_img, self.next_hover)
                rect = img.get_rect(center=base_rect.center)
            else:
                img = pygame.transform.scale(self.next_img, self.next_base)
                rect = img.get_rect(topleft=base_rect.topleft)

            self.SCREEN.blit(img, rect)

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if rect.collidepoint(mouse):
                        self.click_sound.play()
                        self.stop_music()
                        self.running = False

    def reset(self):
        self.current_question = 0
        self.score = 0
        self.selected = None
        self.state = "quiz"
        self.played_sound = False

    # ---------------- MAIN LOOP ----------------
    def run(self):
        clock = pygame.time.Clock()
        self.running = True

        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.stop_music()
                    self.running = False

            if self.state == "quiz":
                self.quiz_screen(events)
            else:
                self.result_screen(events)

            pygame.display.update()
            clock.tick(60)

        self.stop_music()

