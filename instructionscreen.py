import pygame
import random
import math

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PIXEL_DARK = (20, 20, 40)

# Neon cycle colors
NEON_COLORS = [
    (255, 80, 80),
    (255, 160, 80),
    (255, 255, 80),
    (80, 255, 140),
    (80, 200, 255),
    (160, 80, 255)
]


class InstructionScreen:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.W = width
        self.H = height

        # Pixel fonts (YOU MUST HAVE a pixel font)
        self.title_font = pygame.font.Font("pixel_font.otf", 56)
        self.text_font = pygame.font.Font("pixel_font.otf", 28)

        # Slide animation
        self.panel_y = height
        self.target_y = 40
        self.slide_speed = 25

        # Scroll
        self.scroll_y = 0
        self.scroll_speed = 25

        # Neon border animation
        self.neon_index = 0
        self.neon_timer = 0

        # Scanlines
        self.scanline_offset = 0

        # Particle sparks around title
        self.particles = []

        # Waving banner animation
        self.wave_offset = 0

        # Text content
        self.lines = [
            "WELCOME TO ROAD SAFETY ADVENTURE!",
            "",
            "• Learn how to stay safe on the road.",
            "• Follow the tutorial steps.",
            "• Answer all quizzes.",
            "• Finish the journey to earn",
            "  the ROAD SAFETY HERO BADGE!",
            "",
            "Press ESC to return to menu."
        ]


    # ----------------------
    #  Background + Scanlines
    # ----------------------
    def draw_background(self):
        overlay = pygame.Surface((self.W, self.H))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        # Scanlines
        self.scanline_offset += 2
        if self.scanline_offset > 8:
            self.scanline_offset = 0

        for y in range(0, self.H, 8):
            scan = pygame.Surface((self.W, 2))
            scan.fill((25, 25, 25))
            scan.set_alpha(40)
            self.screen.blit(scan, (0, y + self.scanline_offset))


    # ----------------------
    # Slide-in panel
    # ----------------------
    def animate_slide(self):
        if self.panel_y > self.target_y:
            self.panel_y -= self.slide_speed
            if self.panel_y < self.target_y:
                self.panel_y = self.target_y


    # ----------------------
    # Neon Border Effect
    # ----------------------
    def draw_neon_border(self, x, y, w, h):
        # update neon color cycle
        self.neon_timer += 1
        if self.neon_timer >= 6:
            self.neon_timer = 0
            self.neon_index = (self.neon_index + 1) % len(NEON_COLORS)

        neon_color = NEON_COLORS[self.neon_index]
        pygame.draw.rect(self.screen, neon_color, (x, y, w, h), 5)


    # ----------------------
    # Title Glow + Particle Sparks
    # ----------------------
    def draw_title(self, y_offset):
        title = self.title_font.render("INSTRUCTIONS", False, WHITE)
        tx = self.W // 2 - title.get_width() // 2
        ty = self.panel_y + 40 + y_offset

        # Title glow background
        glow = pygame.Surface((title.get_width() + 30, title.get_height() + 10))
        glow.fill((255, 200, 50))
        glow.set_alpha(90)
        self.screen.blit(glow, (tx - 15, ty - 5))

        # Render actual title
        self.screen.blit(title, (tx, ty))

        # Emit sparks
        if random.random() < 0.3:
            self.particles.append([
                tx + random.randint(-20, title.get_width() + 20),
                ty + random.randint(0, title.get_height()),
                random.uniform(-1.5, 1.5),
                random.uniform(-3, -1),
                random.randint(5, 8)
            ])

        # Draw sparks
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[4] -= 0.3
            if p[4] <= 0:
                self.particles.remove(p)
            else:
                pygame.draw.rect(self.screen, (255, 255, 120),
                                 (p[0], p[1], 3, 3))


    # ----------------------
    # Waving Pixel Banner
    # ----------------------
    def draw_wave_banner(self):
        self.wave_offset += 0.15

        for x in range(0, self.W, 14):
            y = int(20 * math.sin((x * 0.05) + self.wave_offset)) + self.panel_y + 5
            pygame.draw.rect(self.screen, (180, 180, 255), (x, y, 12, 6))


    # ----------------------
    # Panel + Text
    # ----------------------
    def draw_panel(self):
        x = 50
        y = self.panel_y
        w = self.W - 100
        h = self.H - 80

        pygame.draw.rect(self.screen, PIXEL_DARK, (x, y, w, h))

        # Neon border
        self.draw_neon_border(x, y, w, h)

        return x + 60, y + 140  # text padding (below title)


    # ----------------------
    # Draw Scrollable Text
    # ----------------------
    def draw_text(self, px, py):
        shake = random.randint(-1, 1) if abs(self.scroll_y) > 0 else 0
        yy = py + self.scroll_y + shake

        for line in self.lines:
            text = self.text_font.render(line, False, WHITE)
            self.screen.blit(text, (px, yy))
            yy += 40


    # ----------------------
    # Scroll Handling
    # ----------------------
    def update_scroll(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * self.scroll_speed
            self.scroll_y = min(0, self.scroll_y)
            self.scroll_y = max(self.scroll_y, -200)


    # ----------------------
    # MAIN DRAW
    # ----------------------
    def draw(self):
        self.animate_slide()
        self.draw_background()
        self.draw_wave_banner()

        px, py = self.draw_panel()
        self.draw_title(self.scroll_y)
        self.draw_text(px, py)
