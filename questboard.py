import pygame
from button import Button

class QuestBoard:

    def __init__(self, screen, sw, sh):
        self.screen = screen
        self.sw = sw
        self.sh = sh

        # -----------------------------
        # LOAD POPUP IMAGE (optional)
        # -----------------------------
        try:
            self.popup = pygame.image.load("quest_board.png").convert_alpha()
        except:
            self.popup = pygame.Surface((540, 360), pygame.SRCALPHA)
            self.popup.fill((215, 205, 175))
            pygame.draw.rect(self.popup, (50, 35, 20), self.popup.get_rect(), 8)

        # -----------------------------
        # LOAD ACCEPT BUTTON ONLY
        # -----------------------------
        self.accept_img = self._load_or_fallback(
            "accept_btn.png",
            (0, 180, 90),
            "ACCEPT QUEST"
        )

        # -----------------------------
        # TEXT FONTS
        # -----------------------------
        try:
            self.font = pygame.font.Font("pixel_font.otf", 32)
            self.body_font = pygame.font.Font("pixel_font.otf", 28)
        except:
            self.font = pygame.font.SysFont("arial", 32)
            self.body_font = pygame.font.SysFont("arial", 28)

        self.text_lines = [
            "QUEST UNLOCKED!",
            "YOUR MISSION:",
            "Help everyone stay safe by learning",
            "and teaching road safety rule!",
            "Accept the quest to continue"
        ]

        self.visible = False
        self._update_button_positions()

    # ------------------------------------------------------
    def _update_button_positions(self):
        popup_w = 540
        popup_h = 360

        px = self.sw // 2 - popup_w // 2
        py = self.sh // 2 - popup_h // 2

        # scale accept button
        scaled_accept = pygame.transform.scale(
            self.accept_img,
            (
                int(self.accept_img.get_width() * 0.38),
                int(self.accept_img.get_height() * 0.38)
            )
        )

        accept_x = px + (popup_w - scaled_accept.get_width()) // 2
        accept_y = py + popup_h - scaled_accept.get_height() - 25

        self.accept_button = Button(
            accept_x,
            accept_y,
            self.accept_img,
            0.38
        )

    # ------------------------------------------------------
    def _load_or_fallback(self, filename, fallback_color, fallback_text):
        try:
            return pygame.image.load(filename).convert_alpha()
        except:
            return self._fallback_surface(240, 80, fallback_color, fallback_text)

    def _fallback_surface(self, w, h, col, text):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill(col)
        pygame.draw.rect(surf, (0, 0, 0), surf.get_rect(), 4)
        try:
            f = pygame.font.Font("pixel_font.otf", 24)
        except:
            f = pygame.font.SysFont("arial", 24)
        ts = f.render(text, True, (255, 255, 255))
        surf.blit(ts, ts.get_rect(center=(w // 2, h // 2)))
        return surf

    # ------------------------------------------------------
    def open(self):
        self.visible = True

    def close(self):
        self.visible = False

    # ------------------------------------------------------
    # DRAW — returns "accept" or None
    # ------------------------------------------------------
    def draw(self):
        if not self.visible:
            return None

        # ----------------------------
        # DARKFADE BACKGROUND
        # ----------------------------
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # ----------------------------
        # POPUP DIMENSIONS
        # ----------------------------
        popup_w = 540
        popup_h = 360
        px = self.sw // 2 - popup_w // 2
        py = self.sh // 2 - popup_h // 2

        # ----------------------------
        # PIXEL POPUP BACKGROUND
        # ----------------------------
        popup = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
        popup.fill((215, 205, 175))  # parchment color

        # thick outer border
        pygame.draw.rect(popup, (50, 35, 20), (0, 0, popup_w, popup_h), 8)

        # inner border
        pygame.draw.rect(popup, (80, 65, 40), (6, 6, popup_w - 12, popup_h - 12), 3)

        # corner pixels (retro effect)
        pygame.draw.rect(popup, (30, 20, 12), (4, 4, 8, 8))
        pygame.draw.rect(popup, (30, 20, 12), (popup_w - 12, 4, 8, 8))
        pygame.draw.rect(popup, (30, 20, 12), (4, popup_h - 12, 8, 8))
        pygame.draw.rect(popup, (30, 20, 12), (popup_w - 12, popup_h - 12, 8, 8))

        # draw popup on screen
        self.screen.blit(popup, (px, py))

        # ----------------------------
        # TITLE TEXT (centered)
        # ----------------------------
        title = self.font.render("QUEST UNLOCKED!", True, (30, 25, 20))
        self.screen.blit(title, (self.sw // 2 - title.get_width() // 2, py + 28))

        # ----------------------------
        # BODY TEXT (centered)
        # ----------------------------
        y = py + 95
        for line in self.text_lines[1:]:  # skip first line, already used as title
            text = self.body_font.render(line, True, (40, 35, 25))
            self.screen.blit(text, (self.sw // 2 - text.get_width() // 2, y))
            y += 38

        # ----------------------------
        # ACCEPT BUTTON
        # ----------------------------
        accept_click = self.accept_button.draw(self.screen)

        if accept_click:
            return "accept"

        return None


