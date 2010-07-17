#!/usr/bin/python
'''Run the game GUI'''
import controller
import display
import game
import geometry
import board
import pygame
import sys
import multilogger
from pygame.locals import *

# Flesh this out when the ability to configure the game is implemented properly
def start_game_simple(screen):
	'''Start a game of Go'''

	#Create grid
	grid = geometry.FoldedGrid(5,5,1,[('N','S'),('E','W')])

	#Create game controller
	game_controller = controller.Controller()
	black = game_controller.add_local_player('black','Black player')
	white = game_controller.add_local_player('white','White player')
	game_controller.begin_game(board.Board(grid))

	#Create GUI
	colors = {black:(0,0,0), white:(200,200,200)}
	view = display.GameGUIPygame(game_controller, screen, (600,300), (10,10), zoom_to_fit=True, join_connected=True, highlight_connected=True,colors=colors)

	#Handle events
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEBUTTONDOWN:
				view.on_click(pygame.mouse.get_pos())

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)

if __name__ == '__main__':

	info('Starting GUI')

	#Initialize pygame
	pygame.init()
	screen = pygame.display.set_mode((620, 320))

	start_game_simple(screen)
