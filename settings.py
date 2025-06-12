import timeit
import pygame
from pyglet import font


pygame.init()
pygame.font.init() 
font_path = "gui/main.ttf"
mainFont = pygame.font.Font(font_path, 18)

monitor = pygame.display.Info()
WIDTH = 927  # monitor.current_w
HEIGHT = 566  # monitor.current_h
MAX_FPS = 100
PAUSE = True
IN_MENU = True
MC_VERSION = "1.0"
clock = pygame.time.Clock()

FOV = 100
RENDER_DISTANCE = 50

CHUNKS_RENDER_DISTANCE = 50
CHUNK_SIZE = (1, 10, 1)
