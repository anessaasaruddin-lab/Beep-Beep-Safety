import pygame
import sys

class TutorialScene:
    def __init__(self, screen, voice_channel):
        self.screen = screen
        self.voice_channel = voice_channel
        self.clock = pygame.time.Clock()
        self.done = False

        # ---------- VOICE ----------
        self.voice = pygame.mixer.Sound("scene1_voice.wav")
        self.voice.set_volume(1.0)
        self.voice_played = False

        # ---------- CLICK SOUND ----------
        self.click_sound = pygame.mixer.Sound("buttonsound.wav")
        self.click_sound.set_volume(0.9)

        # ---------- BACKGROUND ----------
        self.background = pygame.image.load("bgdilah.png").convert()
        self.background = pygame.transform.scale(
            self.background,
            (self.screen.get_width(), self.screen.get_height())
        )

        # ---------- ASSETS ----------
        self.sprite_sheet = pygame.image.load("speak2.png").convert_alpha()
        self.dialog_box = pygame.image.load("dialog.png").convert_alpha()
        self.next_img = pygame.image.load("next.png").convert_alpha()
        self.font = pygame.font.Font("pixel_font.otf", 28)

        # ---------- NPC ----------
        self.sprite_sheet = pygame.transform.rotozoom(self.sprite_sheet, 0, 0.8)
        frame_w = self.sprite_sheet.get_width() // 4
        frame_h = self.sprite_sheet.get_height()

        self.frames = [
            self.sprite_sheet.subsurface((i * frame_w, 0, frame_w, frame_h))
            for i in range(4)
        ]

        self.current_frame = 0
        self.frame_timer = 0
        self.FRAME_DELAY = 24

        # ---------- TEXT ----------
        self.text = (
            "Hi! I'm Officer Lina. Before you head outside, "
            "let's learn some important safety tips to keep you protected and aware."
        )

        self.typing_index = 0
        self.text_timer = 0
        self.text_delay = 3
        self.displayed_text = ""
        self.show_next = False

        # ---------- DIALOG POP ANIMATION ----------
        self.dialog_scale = 0.0
        self.dialog_pop_speed = 0.015

        # ---------- NEXT BUTTON ----------
        self.next_base_size = (70, 70)
        self.next_hover_size = (85, 85)

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

    def run(self):
        while not self.done:

            # ▶️ PLAY VOICE ONCE
            if not self.voice_played:
                self.voice_channel.play(self.voice)
                self.voice_played = True

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.voice_channel.stop()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_next and self.next_rect.collidepoint(event.pos):
                        self.click_sound.play()
                        self.voice_channel.stop()
                        self.done = True

            # ---------- NPC ANIMATION ----------
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_DELAY:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.frame_timer = 0

            # ---------- DIALOG POP ----------
            if self.dialog_scale < 1.0:
                self.dialog_scale += self.dialog_pop_speed
                self.dialog_scale = min(self.dialog_scale, 1.0)

            # ---------- TEXT TYPING (AFTER POP) ----------
            if self.dialog_scale >= 1.0:
                if self.typing_index < len(self.text):
                    self.text_timer += 1
                    if self.text_timer >= self.text_delay:
                        self.typing_index += 1
                        self.displayed_text = self.text[:self.typing_index]
                        self.text_timer = 0
                    self.show_next = False
                else:
                    self.displayed_text = self.text
                    self.show_next = True

            # ---------- DRAW ----------
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.frames[self.current_frame], (70, 280))

            # ---------- DIALOG POP DRAW ----------
            target_w, target_h = 750, 310
            pop_w = int(target_w * self.dialog_scale)
            pop_h = int(target_h * self.dialog_scale)

            dialog_img = pygame.transform.scale(self.dialog_box, (pop_w, pop_h))
            pop_x = 150 + (target_w - pop_w) // 2
            pop_y = 50 + (target_h - pop_h) // 2
            self.screen.blit(dialog_img, (pop_x, pop_y))

            # ---------- TEXT ----------
            if self.dialog_scale >= 1.0:
                y = 150
                for line in self.wrap_text(self.displayed_text, self.font, 500):
                    self.screen.blit(
                        self.font.render(line, True, (0, 0, 0)),
                        (300, y)
                    )
                    y += 32

            # ---------- NEXT BUTTON ----------
            if self.show_next:
                base_rect = pygame.Rect(700, 420, *self.next_base_size)

                if base_rect.collidepoint(mouse_pos):
                    next_img = pygame.transform.scale(
                        self.next_img, self.next_hover_size
                    )
                    self.next_rect = next_img.get_rect(center=base_rect.center)
                else:
                    next_img = pygame.transform.scale(
                        self.next_img, self.next_base_size
                    )
                    self.next_rect = next_img.get_rect(topleft=(700, 420))

                self.screen.blit(next_img, self.next_rect)

            pygame.display.flip()
            self.clock.tick(60)




