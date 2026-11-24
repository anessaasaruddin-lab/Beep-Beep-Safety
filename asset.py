import pygame

def load_assets(WIDTH, HEIGHT):
    assets = {}

    assets["background"] = pygame.transform.scale(
        pygame.image.load("background.png").convert(), (WIDTH, HEIGHT)
    )

    assets["dialog"] = pygame.image.load("dialog.png").convert_alpha()
    assets["next"] = pygame.image.load("next.png").convert_alpha()
    assets["card_bg"] = pygame.image.load("cardbackground.png").convert()
    assets["takequiz"] = pygame.image.load("takequiz.png").convert_alpha()

    assets["cards"] = {
        1: pygame.image.load("card1.png").convert_alpha(),
        2: pygame.image.load("card2.png").convert_alpha(),
        3: pygame.image.load("card3.png").convert_alpha(),
    }

    assets["flashbacks"] = {
        1: pygame.image.load("flashcard1.png").convert_alpha(),
        2: pygame.image.load("flashcard2.png").convert_alpha(),
        3: pygame.image.load("flashcard3.png").convert_alpha(),
    }

    assets["lesson_bg"] = pygame.transform.scale(
        pygame.image.load("flashcardbackground2.png").convert(), (WIDTH, HEIGHT)
    )

    assets["sounds"] = {
        "scene1": pygame.mixer.Sound("scene1_voice.wav"),
        "flip": pygame.mixer.Sound("flipcardsound.wav"),
        "hover": pygame.mixer.Sound("hoversound.wav"),
        "button": pygame.mixer.Sound("buttonsound.wav"),
        "pop": pygame.mixer.Sound("dialog_pop.wav"),
        "lesson1": pygame.mixer.Sound("scene10_voice.wav"),
        "lesson2": pygame.mixer.Sound("scene11_voice.wav"),
        "lesson3": pygame.mixer.Sound("scene12_voice.wav"),
        "complete": pygame.mixer.Sound("scene13_voice.wav"),
        "quiz": pygame.mixer.Sound("button2sound.wav"),
    }

    return assets
