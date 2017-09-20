import pygame
pygame.init()
song = pygame.mixer.Sound('./song.mp3')
clock = pygame.time.Clock()
song.play()
while True:
    clock.tick(60)
pygame.quit()
