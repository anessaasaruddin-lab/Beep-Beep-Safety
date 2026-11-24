import pygame
import os
import random
import math
import sys

class GoodJobScene:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.clock = pygame.time.Clock()
        self.running = True

        # -------- ASSET PATH HANDLING --------
        # Works for both development & PyInstaller EXE
        if getattr(sys, 'frozen', False):
            self.asset_dir = os.path.dirname(sys.executable)    # dist/home
        else:
            self.asset_dir = os.path.dirname(os.path.abspath(__file__))  # dev folder

        def asset(name):
            return os.path.join(self.asset_dir, name)

        # -------- SOUND INIT --------
        pygame.mixer.init()

        # -------- FONTS --------
        self.pixel_font = pygame.font.Font(asset("BoldPixels.ttf"), 100)
        self.pixel_font_small = pygame.font.Font(asset("BoldPixels.ttf"), 33)

        # -------- LOAD HELPERS --------
        def load_image(filename, scale=None):
            path = asset(filename)
            if not os.path.exists(path):
                print("IMAGE MISSING:", path)
                return None
            img = pygame.image.load(path).convert_alpha()
            if scale:
                img = pygame.transform.scale(img, scale)
            return img

        def load_sound(filename):
            path = asset(filename)
            if not os.path.exists(path):
                print("SOUND MISSING:", path)
                return None
            return pygame.mixer.Sound(path)

        # -------- IMAGES --------
        self.flashcard_bg = load_image("flashcardbackground2.png", (self.WIDTH, self.HEIGHT))

        textbox_w, textbox_h = 750, 450
        self.textbox_bg = load_image("yellowtextbox.png", (textbox_w, textbox_h))
        self.textbox_pos = ((self.WIDTH - textbox_w)//2, (self.HEIGHT - textbox_h)//2)

        self.badge_img = load_image("buttonbadge.png")
        if self.badge_img:
            self.badge_img = pygame.transform.scale(self.badge_img, (150, 150))

        self.back_btn_rect = pygame.Rect(400, 400, 100, 100)
        self.back_img = load_image("backmainmenu.png", self.back_btn_rect.size)

        # -------- SOUNDS --------
        self.typing_sound = load_sound("typewrittersound.wav")
        self.achievement_sound = load_sound("achievement.wav")
        self.button_click_sound = load_sound("click.wav")
        self.badge_sound = load_sound("woosh.wav")

        self.typing_channel = pygame.mixer.Channel(1)
        self.click_channel = pygame.mixer.Channel(2)
        self.badge_channel = pygame.mixer.Channel(3)
        self.achievement_channel = pygame.mixer.Channel(4)

        # -------- ANIMATION STATE --------
        self.scroll_x = 0
        self.scroll_speed = 2

        self.badge_x = self.WIDTH//2 + 100
        self.badge_y = -200
        self.badge_target_y = 290
        self.badge_speed = 10
        self.badge_sound_played = False

        self.lines = [
            "Congrats! You have completed the quest",
            "in SafeVille!",
            "You have been rewarded the",
            "Road Rangers Badge!",
        ]

        self.rendered_lines = [""] * len(self.lines)
        self.current_line_index = 0
        self.current_char_index = 0
        self.typing_delay = 50
        self.last_typing_time = pygame.time.get_ticks()

        self.title_done = False
        self.text_done = False
        self.back_button_visible = False
        self.back_hover_played = False

        self.achievement_start_time = pygame.time.get_ticks()
        if self.achievement_sound:
            self.achievement_channel.play(self.achievement_sound)

    # =====================================================
    def run(self):
        while self.running:
            self.screen.fill((0, 0, 0))
            now = pygame.time.get_ticks()

            # -------- BACKGROUND SCROLL --------
            if self.flashcard_bg:
                self.scroll_x -= self.scroll_speed
                if self.scroll_x <= -self.WIDTH:
                    self.scroll_x = 0
                self.screen.blit(self.flashcard_bg, (self.scroll_x, 0))
                self.screen.blit(self.flashcard_bg, (self.scroll_x + self.WIDTH, 0))

            if self.textbox_bg:
                self.screen.blit(self.textbox_bg, self.textbox_pos)

            # -------- TITLE --------
            if now - self.achievement_start_time < 1500:
                for _ in range(2):
                    ox = random.randint(-2, 2)
                    oy = random.randint(-2, 2)
                    color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
                    title = self.pixel_font.render("GOOD JOB!", True, color)
                    self.screen.blit(title, (225+ox, 110+oy))
            else:
                title = self.pixel_font.render("GOOD JOB!", True, (0,0,0))
                self.screen.blit(title, (225,110))
                self.title_done = True
                if self.achievement_channel.get_busy():
                    self.achievement_channel.stop()

            # -------- TYPEWRITER TEXT --------
            if self.title_done and not self.text_done:
                if self.current_line_index < len(self.lines):
                    line = self.lines[self.current_line_index]
                    if now - self.last_typing_time > self.typing_delay:
                        if self.current_char_index < len(line):
                            self.rendered_lines[self.current_line_index] = line[:self.current_char_index+1]
                            self.current_char_index += 1
                            self.last_typing_time = now
                            if self.typing_sound:
                                self.typing_channel.play(self.typing_sound)
                        else:
                            self.current_line_index += 1
                            self.current_char_index = 0
                            self.last_typing_time = now
                else:
                    self.text_done = True
                    self.back_button_visible = True
                    if self.typing_channel.get_busy():
                        self.typing_channel.stop()

            # -------- DRAW TEXT --------
            for i, rline in enumerate(self.rendered_lines):
                rendered = self.pixel_font_small.render(rline, True, (0,0,0))
                self.screen.blit(rendered, (150, 220 + i*40))

            # -------- BADGE --------
            if self.text_done and self.badge_img:
                if self.badge_y < self.badge_target_y:
                    self.badge_y += self.badge_speed
                else:
                    self.badge_y = self.badge_target_y
                    if self.badge_sound and not self.badge_sound_played:
                        self.badge_channel.play(self.badge_sound)
                        self.badge_sound_played = True

                glow = pygame.Surface(
                    (self.badge_img.get_width()+20, self.badge_img.get_height()+20),
                    pygame.SRCALPHA
                )
                alpha = 80 + 50*math.sin(pygame.time.get_ticks()*0.005)
                pygame.draw.ellipse(glow, (255,255,150,int(alpha)), glow.get_rect())
                self.screen.blit(glow, (self.badge_x-10, self.badge_y-10))
                self.screen.blit(self.badge_img, (self.badge_x, self.badge_y))

            # -------- BACK BUTTON --------
            mouse_pos = pygame.mouse.get_pos()
            if self.back_button_visible and self.back_img:
                hovering = self.back_btn_rect.collidepoint(mouse_pos)
                if hovering:
                    scale = pygame.transform.scale(
                        self.back_img,
                        (int(self.back_img.get_width()*1.1), int(self.back_img.get_height()*1.1))
                    )
                    self.screen.blit(scale, (self.back_btn_rect.x-5, self.back_btn_rect.y-5))
                    if not self.back_hover_played:
                        if self.button_click_sound:
                            self.click_channel.play(self.button_click_sound)
                        self.back_hover_played = True
                else:
                    self.screen.blit(self.back_img, self.back_btn_rect)
                    self.back_hover_played = False

            # -------- EVENTS --------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_btn_rect.collidepoint(event.pos):
                        if self.button_click_sound:
                            self.click_channel.play(self.button_click_sound)
                        self.running = False

            pygame.display.flip()
            self.clock.tick(60)

        # Returning to caller to go back to main menu
        return "main"


