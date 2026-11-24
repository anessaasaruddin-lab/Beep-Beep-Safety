import pygame
import sys

class LessonScene3:
    def __init__(self, screen, voice_channel):
        self.screen = screen
        self.voice_channel = voice_channel
        self.clock = pygame.time.Clock()
        self.done = False

        # ---------- ASSETS ----------
        self.lesson_bg = pygame.image.load("flashcardbackground2.png").convert()
        self.lesson_bg = pygame.transform.scale(
            self.lesson_bg, (screen.get_width(), screen.get_height())
        )

        self.sprite_sheet = pygame.image.load("speak2.png").convert_alpha()
        self.dialog_box = pygame.image.load("dialog.png").convert_alpha()
        self.next_img = pygame.image.load("next.png").convert_alpha()
        self.flash_back = pygame.image.load("flashcard3.png").convert_alpha()

        self.font = pygame.font.Font("pixel_font.otf", 28)

        # ---------- VOICE ----------
        self.voice = pygame.mixer.Sound("scene12_voice.wav")
        self.voice.set_volume(1.0)
        self.voice_played = False

        # ---------- CLICK SOUND ----------
        self.click_sound = pygame.mixer.Sound("buttonsound.wav")
        self.click_sound.set_volume(0.9)

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
        self.lesson_text = "Keep your eyes on the road and not on the phone!"

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
                    if self.next_rect.collidepoint(event.pos):
                        self.click_sound.play()
                        self.voice_channel.stop()
                        self.done = True

            # ---------- NPC ANIMATION ----------
            self.frame_timer += 1
            if self.frame_timer >= self.FRAME_DELAY:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.frame_timer = 0

            # ---------- DRAW ----------
            self.screen.blit(self.lesson_bg, (0, 0))
            self.screen.blit(self.frames[self.current_frame], (40, 270))

            card = pygame.transform.scale(self.flash_back, (485, 278))
            self.screen.blit(card, card.get_rect(center=(560, 213)))

            dialog = pygame.transform.scale(self.dialog_box, (750, 310))
            self.screen.blit(dialog, (175, 330))

            y = 430
            for line in self.wrap_text(self.lesson_text, self.font, 450):
                self.screen.blit(
                    self.font.render(line, True, (0, 0, 0)),
                    (320, y)
                )
                y += 32

            # ---------- NEXT BUTTON (HOVER EFFECT ONLY) ----------
            base_rect = pygame.Rect(750, 475, *self.next_base_size)

            if base_rect.collidepoint(mouse_pos):
                next_img = pygame.transform.scale(
                    self.next_img, self.next_hover_size
                )
                self.next_rect = next_img.get_rect(center=base_rect.center)
            else:
                next_img = pygame.transform.scale(
                    self.next_img, self.next_base_size
                )
                self.next_rect = next_img.get_rect(topleft=(750, 475))

            self.screen.blit(next_img, self.next_rect)

            pygame.display.flip()
            self.clock.tick(60)



