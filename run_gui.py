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

# Flesh this out when the ability to configure the game is implemented properly. Later, this function or something similar will be called from within the GUI when the user chooses to begin a game.
def start_game_simple():
	'''Start a game of Go'''

	#Create grid
	grid = geometry.FoldedGrid(5,5,1,[('N','S'),('E','W')])

	#Create game controller
	game_controller = controller.Controller()
	black = game_controller.add_local_player('black','Black player')
	white = game_controller.add_local_player('white','White player')
	game_controller.begin_game(board.Board(grid))

	return game_controller,black,white

def start_game_pygame():
	'''Use pygame to display a game of Go'''
	pygame.init()
	screen = pygame.display.set_mode((620, 320))

	game_controller,black,white = start_game_simple()

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

def start_game_wx():
	'''Use wxPython to display a game of go'''
	game_controller,black,white = start_game_simple()
	colors = {black:(0,0,0), white:(200,200,200)}
	app = display.GoApp(game_controller, colors)
	app.MainLoop()

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)

if __name__ == '__main__':

	info('Starting GUI')

	if len(sys.argv) > 1 and sys.argv[1].lower() == 'pygame':
		start_game_pygame()
	else:
		start_game_wx()
