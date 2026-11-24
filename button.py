import pygame
import math

class Button:
    def __init__(self, x, y, image, scale, hover_scale=1.15, hover_distance=80):
        # Base image
        width = image.get_width()
        height = image.get_height()
        self.base_image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))

        self.image = self.base_image
        self.rect = self.image.get_rect(topleft=(x, y))

        # Hover effect
        self.hover_scale = hover_scale         # How much bigger the button becomes
        self.hover_distance = hover_distance   # How close the mouse needs to be

        # Click state
        self.clicked = False

    def draw(self, surface):
        action = False
        mouse_pos = pygame.mouse.get_pos()

        # Distance from mouse to button center
        dist = math.dist(mouse_pos, self.rect.center)

        # Hover effect: if mouse is near, scale up
        if dist < self.hover_distance:
            new_size = (
                int(self.base_image.get_width() * self.hover_scale),
                int(self.base_image.get_height() * self.hover_scale)
            )
            self.image = pygame.transform.scale(self.base_image, new_size)
            # Re-center after resizing
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            # Reset to base size
            center = self.rect.center
            self.image = self.base_image
            self.rect = self.image.get_rect(center=center)

        # Click detection
        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # Draw button
        surface.blit(self.image, self.rect.topleft)
        return action
