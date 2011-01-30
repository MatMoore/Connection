#!/usr/bin/python
'''This module contains the underlying model of the game itself. It depends heavily on the board and rules modules. Games are currently limited to two players only.

There are four major stages to the game, represented by module level constants:

	`game.GAME_HANDICAP`
		The current player must place handicap stones before the game can begin.
	`game.PLAY_GAME`
		The game is in progress.
	`game.MARK_DEAD`
		The game is over, and players must mark the "dead" stones.
	`game.GAME_OVER`
		The game is over.
'''

from observer import Observable
from copy import copy
import string
import rules
import geometry
import multilogger

# Game states
PLACE_HANDICAP = 0
PLAY_GAME = 1
MARK_DEAD = 2
GAME_OVER = 3

# Define some exceptions
class GameError(Exception):
	'''Base class for all Game exceptions.'''
	pass

class NotYourTurnError(GameError):
	'''Thrown when a player makes a move when it's not their turn.'''
	pass

class GameOverError(GameError):
	'''Thrown if the operation is invalid because the game is over.'''
	pass

class TwoPlayerGame(Observable):
	'''This class creates the core object representing the state of the game. The current state of the game is given by the value of the `state` attribute.

	The typical lifecycle of this object is as follows:

1. Play moves using play_move, pass_turn, and resign. (state = `PLAY_GAME` or `PLACE_HANDICAP`).

2. If the game ends with neither player resigning, the game state will change to `MARK_DEAD`.

3. Mark any dead stones using the game's board object directly

4. When all dead stones have been marked, call score to end the game (`GAME_OVER` state) and calculate who won.
	'''

	def __init__(self,board,black_player=None,white_player=None,fixed_handicap=0,komi=0,custom_handicap=0,ruleset=None):
		info('Starting game')

		Observable.__init__(self)
		self.board = board

		if ruleset:
			self.ruleset = ruleset
		else:
			self.ruleset = rules.AGARules()

		self.history = [] # the board at all times in the past
		self.moves = [] # the list of moves

		if black_player is None:
			black_player = Player('black','Black')
		if white_player is None:
			white_player = Player('black','Black',komi=komi)

		self.black = black_player
		self.white = white_player
		self.next_player = self.black
		self.winner = None
		self.state = PLACE_HANDICAP

		self.ruleset.setup(self)

	def start(self):
		self.state = PLAY_GAME

	def end(self):
		if self.state != MARK_DEAD and self.winner is None:
			self.state = MARK_DEAD
		else:
			self.state = GAME_OVER

	def last_move(self):
		'''Return the last move played.'''
		if self.moves:
			return self.moves[-1]

	def play_move(self,position,player):
		'''Attempt to play the next move or handicap stone.'''

		if self.state in (GAME_OVER, MARK_DEAD):
			raise GameOverError

		if player is not self.next_player:
			raise NotYourTurnError

		move = Move(position, player)

		# Attempt to play the move
		if self.state == PLAY_GAME:
			self.ruleset.play_move(move)
		elif self.state == PLACE_HANDICAP:
			self.ruleset.place_handicap(move)

		# Raise an exception if the move was invalid
		# TODO: fix the GUI to display the list of errors instead of using exceptions
		self.ruleset.errors.check()

		# Update the game state
		if self.state == PLACE_HANDICAP:
			self.end_place_handicap()
		elif self.state == PLAY_GAME:
			# Save the board state and move for later
			self.moves.append(move)
			self.history.append(copy(self.board))

			self.end_turn()

		self.notify(move)

	def end_turn(self):
		'''Check for game over and change player'''
		info('ending turn')
		if self.ruleset.gameover():
			self.end()
		else:
			# Change the active player of the current team
			self.ruleset.change_active_player()

			# Now it is the next team's turn
			self.ruleset.change_team()

	def end_place_handicap(self):
		'''Check if handicap placement is complete and handle changing players'''
		debug('end_place_handicap')
		# Change the active player of the current team
		self.ruleset.change_active_player()

		if not self.ruleset.more_handicap(self.next_player):
			# Now it is the next team's turn
			self.ruleset.change_team()

			# If everyone is done placing handicaps, start the game
			if all(map(self.ruleset.more_handicap, (self.black,self.white))):
				self.start()

	def pass_turn(self):
		'''Pass turn.'''
		if self.state in (GAME_OVER, MARK_DEAD):
			raise GameOverError

		if self.state == PLACE_HANDICAP:
			# Do nothing
			return

		move = SpecialMove('pass',self.next_player)
		self.moves.append(move)

		self.end_turn()
		self.notify(move)

	def resign(self):
		'''Resign the game.'''
		if self.state in (GAME_OVER, MARK_DEAD):
			raise GameOverError

		if self.next_player == self.black:
			self.winner = self.white
		else:
			self.winner = self.black

		move = SpecialMove('resign',self.next_player)
		self.moves.append(move)
		self.end()
		self.notify(move)

	def score(self):
		'''Score the game.'''
		debug('Scoring')
		self.board.mark_territory()
		territory = self.board.count_territory()

		for player in self.players:
			self.ruleset.score_player(player, territory.setdefault(player,0))

		debug('dsff')
		if self.black.score > self.white.score:
			self.winner = self.black
		elif self.black.score < self.white.score:
			self.winner = self.white
		else:
			self.winner = None # Jigo
		debug('ending')
		self.end()
		self.notify(None)

	@property
	def players(self):
		'''A tuple of the black and white player objects.'''
		return self.black,self.white

	@property
	def state(self):
		'''Integer representing the current game stage.'''
		return self._game_state


class Player:
	'''Stores information about a player.'''
	def __init__(self,color,name=None,komi=0):
		self.color = color
		if name:
			self.name = name
		else:
			self.name = color
		self.captures = 0
		self.score = 0
		self.komi = komi

class Move:
	'''Stores information about a move.'''
	def __init__(self,position,player):
		self.type = 'move'
		self.position = position
		self.player = player

	# TODO: fix this to be more reliable.
	# Create a seperate function for GTP representation
	# if the board is compatable
	def __str__(self):
		'''Format: [color] [letter][number]'''
		d = int(self.position[0])
		letters = [l for l in string.ascii_uppercase if l is not 'I']
		x = letters[d]
		y = self.position[1] + 1
		return '%s %s%d'%(self.player.color,x,y)

class SpecialMove:
	'''Represents a pass/resign move.'''
	def __init__(self,type,player):
		self.type = type
		self.player = player
		self.position = (-1,-1)

	def __str__(self):
		return '%s %s'%(self.player.color,self.type)

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
