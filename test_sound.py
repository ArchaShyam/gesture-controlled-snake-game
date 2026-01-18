import pygame
pygame.init()
pygame.mixer.init()
sound = pygame.mixer.Sound("assets/eat.wav")
sound.play()
input("Press enter to exit")
