#!/usr/bin/python
'''The game logic for a two player game of go.

General usage is as follows:

1. Play moves using play_move, pass_turn, and resign. (Game state = PLAY_GAME or PLACE_HANDICAP)

2. If the game ends with neither player resigning, the game state will change to MARK_DEAD.

3. Mark any dead stones using the game's board object directly

4. When all dead stones have been marked, call score to end the game (GAME_OVER state) and calculate who won.'''

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
class GameError(Exception): pass

class NotYourTurnError(GameError):
	'''Thrown when a player makes a move when it's not their turn'''
	pass

class GameOverError(GameError):
	pass

class TwoPlayerGame(Observable):
	'''Handles all the game logic for a 2 player game of go.'''

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
			white_player = Player('black','Black')

		self.black = black_player
		self.white = white_player
		self.winner = None

		if fixed_handicap or custom_handicap:
			self.handicap = fixed_handicap + custom_handicap
		else:
			self.handicap = 0

		if fixed_handicap:
			placed_stones = ruleset.place_handicap(fixed_handicap,self.board,self.black)
			if placed_stones < fixed_handicap:
				custom_handicap += fixed_handicap - placed_stones

		if custom_handicap:
			self.remaining_handicap = custom_handicap
		else:
			self.remaining_handicap = 0

		# Black goes first, unless they have a handicap
		if self.handicap and self.remaining_handicap == 0:
			self.next_player = self.white
		else:
			self.next_player = self.black

		# Extra points to compensate white for black going first
		self.komi = komi

		self._game_state = None
		self._change_game_state()

	def last_move(self):
		'''Return the last move played'''
		if self.moves:
			return self.moves[-1]

	def change_player(self):
		'''Toggle the next player'''
		if self.next_player == self.black:
			self.next_player = self.white
		else:
			self.next_player = self.black

	def current_player(self):
		'''Return the id of the current player'''
		return self.next_player.color

	def play_move(self,position,player):
		'''Attempt to play the next move'''

		if self.state in (GAME_OVER, MARK_DEAD):
			raise GameOverError

		if player is not self.next_player:
			raise NotYourTurnError

		move = Move(position, player)

		# Check the move doesn't break the rules (will raise an exception if it does)
		self.ruleset.check_rules(move,self.board,self.history)

		# Play the move
		self.board.place_stone(move)
		player.captures += self.board.remove_dead_stones(move)

		# Save the board state and move for later
		self.moves.append(move)
		self.history.append(copy(self.board))

		# If this is a handicap stone, then it might still be the current player's turn
		if not self.remaining_handicap:
			self.change_player()
		else:
			self.remaining_handicap -= 1

		self._change_game_state()
		self.notify(move)

	def pass_turn(self):
		'''Pass turn. If both players pass the game is over.'''
		if self.state in (GAME_OVER, MARK_DEAD):
			raise GameOverError

		move = SpecialMove('pass',self.next_player)
		self.moves.append(move)
		self.change_player()
		self._change_game_state()
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
		self._change_game_state()
		self.notify(move)

	def score(self):
		debug('Scoring')
		self.ruleset.score(self.board, self.black, self.white, self.komi)
		if self.black.score > self.white.score:
			self.winner = self.black
		elif self.black.score < self.white.score:
			self.winner = self.white
		else:
			self.winner = None # Jigo
		self._game_state = GAME_OVER
		self.notify(None)

	@property
	def players(self):
		return self.black,self.white

	@property
	def state(self):
		return self._game_state

	def _change_game_state(self):
		'''Update the game state after each move'''
		if self._game_state == GAME_OVER:
			return

		if self.winner:
			debug('Game over')
			self._game_state = GAME_OVER

		# Mark dead stones
		elif self.ruleset.game_over(self.moves,self.white,self.black):
			debug('Mark dead stones')
			self._game_state = MARK_DEAD

		# Free placement of handicap stones
		elif self.remaining_handicap:
			self._game_state = PLACE_HANDICAP

		else:
			self._game_state = PLAY_GAME

class Player:
	'''Stores information about a player'''
	def __init__(self,color,name=None):
		self.color = color
		if name:
			self.name = name
		else:
			self.name = color
		self.captures = 0
		self.score = 0

class Move:
	'''Stores information about a move'''
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
	'''Represents a pass/resign move'''
	def __init__(self,type,player):
		self.type = type
		self.player = player
		self.position = (-1,-1)

	def __str__(self):
		return '%s %s'%(self.player.color,self.type)

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
