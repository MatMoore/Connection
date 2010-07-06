import controller
import display
import game
import geometry
import board
import pygame
import sys
from pygame.locals import *

# Flesh this out when the ability to configure the game is implemented properly
def start_game_simple(screen):

	#Create grid
	grid = geometry.FoldedGrid(5,5,1,[('N','S'),('E','W')])
	game_controller = controller.Controller()
	black = game_controller.add_local_player('black','Black player')
	white = game_controller.add_local_player('white','White player')
	game_controller.begin_game(board.Board(grid))

	colors = {black:(0,0,0),white:(100,100,100)}
	view = display.GameViewPygame(game_controller, screen, zoom_to_fit=True, join_connected=True, highlight_connected=True,colors=colors)
#	view = display.GridViewPygame(grid, screen, zoom_to_fit=True, join_connected=True, highlight_connected=True,colors=colors)

	#Handle events
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				view.on_click(pygame.mouse.get_pos())

if __name__ == '__main__':

	#Initialize pygame
	pygame.init()
	screen = pygame.display.set_mode((600, 300))

	start_game_simple(screen)
