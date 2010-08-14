#!/usr/bin/python
'''The game logic for a two player game of go'''
from observer import Observable
from copy import copy
import string
import rules
import geometry
import multilogger

# Define some exceptions
class GameError(Exception): pass

class NotYourTurnError(GameError):
	'''Thrown when a player makes a move when it's not their turn'''
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

		self.notify(move)

	def pass_turn(self):
		'''Pass turn. If both players pass the game is over.'''
		move = SpecialMove('pass',self.next_player)
		self.moves.append(move)
		self.change_player()
		self.notify(move)

	def resign(self):
		'''Resign the game.'''
		if self.next_player == self.black:
			self.winner = self.white
		else:
			self.winner = self.black

		move = SpecialMove('resign',self.next_player)
		self.moves.append(move)
		self.notify(move)

	@property
	def players(self):
		return self.black,self.white


class Player:
	'''Stores information about a player'''
	def __init__(self,color,name=None):
		self.color = color
		if name:
			self.name = name
		else:
			self.name = color
		self.captures = 0

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
