import pygame
import sys

class FlashcardScene:
    def __init__(self, screen, flip_channel):
        self.screen = screen
        self.flip_channel = flip_channel

        self.clock = pygame.time.Clock()
        self.done = False
        self.next_scene = None

        # ---------- FLIP TIMING ----------
        self.flip_duration = 2.0
        self.flip_elapsed = 0.0

        # ---------- SOUND ----------
        self.flip_sound = pygame.mixer.Sound("flipcardsound.wav")
        self.flip_sound.set_volume(0.9)

        self.hover_sound = pygame.mixer.Sound("hoversound.wav")
        self.hover_sound.set_volume(5.0)

        # ---------- ASSETS ----------
        self.card_bg = pygame.image.load("cardbackground.png").convert()

        self.card1 = pygame.image.load("card1.png").convert_alpha()
        self.card2 = pygame.image.load("card2.png").convert_alpha()
        self.card3 = pygame.image.load("card3.png").convert_alpha()

        self.flash_back_1 = pygame.image.load("flashcard1.png").convert_alpha()
        self.flash_back_2 = pygame.image.load("flashcard2.png").convert_alpha()
        self.flash_back_3 = pygame.image.load("flashcard3.png").convert_alpha()

        self.font = pygame.font.Font("pixel_font.otf", 40)

        # ---------- CARD POSITIONS ----------
        self.card_w, self.card_h = 200, 260
        self.hover_scale = 1.08
        self.hover_padding = 40  # NEAR hover radius

        self.card1_thumb = pygame.transform.scale(self.card1, (self.card_w, self.card_h))
        self.card2_thumb = pygame.transform.scale(self.card2, (self.card_w, self.card_h))
        self.card3_thumb = pygame.transform.scale(self.card3, (self.card_w, self.card_h))

        self.card1_rect = self.card1_thumb.get_rect(center=(200, 300))
        self.card2_rect = self.card2_thumb.get_rect(center=(450, 300))
        self.card3_rect = self.card3_thumb.get_rect(center=(700, 300))

        # ---------- HOVER STATE ----------
        self.card1_near = False
        self.card2_near = False
        self.card3_near = False

        # ---------- FLIP STATE ----------
        self.flipping = False
        self.flip_angle = 0
        self.selected_card = None

    # ---------- NEAR HOVER SOUND ----------
    def handle_hover_sound(self, rect, was_near):
        mouse_pos = pygame.mouse.get_pos()

        near_rect = rect.inflate(self.hover_padding * 2,
                                 self.hover_padding * 2)

        is_near = near_rect.collidepoint(mouse_pos)

        if is_near and not was_near and not self.flipping:
            self.hover_sound.play()

        return is_near

    # ---------- VISUAL HOVER ----------
    def draw_hover_card(self, img, rect, mouse_pos):
        if rect.collidepoint(mouse_pos):
            scaled = pygame.transform.scale(
                img,
                (int(self.card_w * self.hover_scale),
                 int(self.card_h * self.hover_scale))
            )
            self.screen.blit(scaled, scaled.get_rect(center=rect.center))
        else:
            self.screen.blit(img, rect)

    def run(self):
        while not self.done:
            dt = self.clock.tick(60) / 1000.0
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.flipping:
                        if self.card1_rect.collidepoint(event.pos):
                            self.start_flip(1)
                        elif self.card2_rect.collidepoint(event.pos):
                            self.start_flip(2)
                        elif self.card3_rect.collidepoint(event.pos):
                            self.start_flip(3)

            # ---------- UPDATE HOVER SOUND ----------
            self.card1_near = self.handle_hover_sound(self.card1_rect, self.card1_near)
            self.card2_near = self.handle_hover_sound(self.card2_rect, self.card2_near)
            self.card3_near = self.handle_hover_sound(self.card3_rect, self.card3_near)

            # ---------- DRAW ----------
            self.screen.blit(self.card_bg, (0, 0))

            title = self.font.render("CHOOSE A CARD", True, (10, 10, 10))
            self.screen.blit(title, (450 - title.get_width() // 2, 40))

            self.draw_hover_card(self.card1_thumb, self.card1_rect, mouse_pos)
            self.draw_hover_card(self.card2_thumb, self.card2_rect, mouse_pos)
            self.draw_hover_card(self.card3_thumb, self.card3_rect, mouse_pos)

            flip_text = self.font.render("TAP TO FLIP", True, (10, 10, 10))
            self.screen.blit(flip_text, (450 - flip_text.get_width() // 2, 480))

            if self.flipping:
                self.animate_flip(dt)

            pygame.display.flip()

    def start_flip(self, card_id):
        self.flipping = True
        self.flip_elapsed = 0.0
        self.flip_angle = 0
        self.selected_card = card_id
        self.flip_channel.play(self.flip_sound)

    def animate_flip(self, dt):
        self.flip_elapsed += dt
        progress = min(self.flip_elapsed / self.flip_duration, 1.0)
        self.flip_angle = progress * 180

        if self.flip_angle <= 90:
            scale = max(1 - self.flip_angle / 90, 0.05)
            showing_front = True
        else:
            scale = (self.flip_angle - 90) / 90
            showing_front = False

        if self.selected_card == 1:
            front, back, rect = self.card1_thumb, self.flash_back_1, self.card1_rect
            self.next_scene = "lesson1"
        elif self.selected_card == 2:
            front, back, rect = self.card2_thumb, self.flash_back_2, self.card2_rect
            self.next_scene = "lesson2"
        else:
            front, back, rect = self.card3_thumb, self.flash_back_3, self.card3_rect
            self.next_scene = "lesson3"

        img = front if showing_front else pygame.transform.scale(back, (self.card_w, self.card_h))
        flipped = pygame.transform.scale(img, (max(1, int(self.card_w * scale)), self.card_h))
        self.screen.blit(flipped, flipped.get_rect(center=rect.center))

        if progress >= 1.0:
            self.flipping = False
            self.done = True
 




