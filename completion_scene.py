import pygame
import sys

class CompletionScene:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.clock = pygame.time.Clock()
        self.done = False
        self.FPS = 10

        # =========================
        # LOAD ASSETS
        # =========================
        self.background = pygame.transform.scale(
            pygame.image.load("bgdilah.png").convert(),
            (self.WIDTH, self.HEIGHT)
        )

        self.dialog_box = pygame.image.load("dialog.png").convert_alpha()
        self.takequiz_btn = pygame.image.load("takequiz.png").convert_alpha()

        self.sprite_sheet = pygame.image.load("speak2.png").convert_alpha()
        self.sprite_sheet = pygame.transform.rotozoom(self.sprite_sheet, 0, 0.8)

        self.scene_voice = pygame.mixer.Sound("scene13_voice.wav")
        self.button_sound = pygame.mixer.Sound("button2sound.wav")
        self.dialog_pop_sound = pygame.mixer.Sound("dialog_pop.wav")

        self.dialog_font = pygame.font.Font("pixel_font.otf", 28)

        # =========================
        # NPC FRAMES
        # =========================
        frame_w = self.sprite_sheet.get_width() // 4
        frame_h = self.sprite_sheet.get_height()

        self.frames = [
            self.sprite_sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
            for i in range(4)
        ]

        self.current_frame = 0
        self.frame_timer = 0
        self.FRAME_DELAY = 6

        # =========================
        # TEXT
        # =========================
        self.final_text = (
            "Great job! You viewed all safety flashcards! "
            "Now let's see what you've learned."
        )

        self.typing_index = 0
        self.typing_speed = 2
        self.displayed_text = ""
        self.show_button = False
        self.voice_played = False

        # =========================
        # DIALOG POP-OUT
        # =========================
        self.dialog_pop_scale = 0.0
        self.dialog_pop_speed = 0.08
        self.dialog_pop_played = False

        self.DIALOG_W, self.DIALOG_H = 750, 310
        self.DIALOG_X, self.DIALOG_Y = 150, 50

    # =========================
    # TEXT WRAP
    # =========================
    def wrap_text(self, text, font, max_width):
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

    # =========================
    # MAIN LOOP
    # =========================
    def run(self):
        while not self.done:
            clicked = False
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clicked = True

            # =========================
            # BACKGROUND
            # =========================
            self.screen.blit(self.background, (0, 0))

            # =========================
            # NPC ANIMATION
            # =========================
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_DELAY:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.frame_timer = 0

            self.screen.blit(self.frames[self.current_frame], (70, 280))

            # =========================
            # DIALOG POP-OUT
            # =========================
            if self.dialog_pop_scale < 1.0:

                if not self.dialog_pop_played:
                    self.dialog_pop_sound.play()
                    self.dialog_pop_played = True

                self.dialog_pop_scale += self.dialog_pop_speed
                self.dialog_pop_scale = min(self.dialog_pop_scale, 1.0)

            pop_w = int(self.DIALOG_W * self.dialog_pop_scale)
            pop_h = int(self.DIALOG_H * self.dialog_pop_scale)

            pop_x = self.DIALOG_X + (self.DIALOG_W - pop_w) // 2
            pop_y = self.DIALOG_Y + (self.DIALOG_H - pop_h) // 2

            dialog_scaled = pygame.transform.scale(self.dialog_box, (pop_w, pop_h))
            self.screen.blit(dialog_scaled, (pop_x, pop_y))

            # =========================
            # TYPING + VOICE
            # =========================
            if self.dialog_pop_scale >= 1.0:

                if self.typing_index == 0 and not self.voice_played:
                    self.scene_voice.play()
                    self.voice_played = True

                if self.typing_index < len(self.final_text):
                    self.typing_index += self.typing_speed
                    self.displayed_text = self.final_text[:self.typing_index]
                else:
                    self.displayed_text = self.final_text
                    self.show_button = True

                y = 150
                for line in self.wrap_text(self.displayed_text, self.dialog_font, 500):
                    self.screen.blit(
                        self.dialog_font.render(line, True, (0, 0, 0)),
                        (300, y)
                    )
                    y += 32

            # =========================
            # ENTER BUTTON (HOVER)
            # =========================
            if self.show_button:
                base_size = (200, 150)
                hover_size = (220, 165)
                base_pos = (615, 370)

                base_rect = pygame.Rect(*base_pos, *base_size)

                if base_rect.collidepoint(mouse_pos):
                    btn = pygame.transform.scale(self.takequiz_btn, hover_size)
                    rect = btn.get_rect(center=base_rect.center)
                else:
                    btn = pygame.transform.scale(self.takequiz_btn, base_size)
                    rect = btn.get_rect(topleft=base_pos)

                self.screen.blit(btn, rect)

                if clicked and rect.collidepoint(mouse_pos):
                    self.button_sound.play()
                    pygame.time.delay(300)
                    self.done = True

            pygame.display.update()
            self.clock.tick(self.FPS)