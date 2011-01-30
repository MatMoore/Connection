#!/usr/bin/python
'''This module implements various rulesets which can be used to validate moves and score the game.'''
from copy import copy
import re
import gameErrors
import game
import board
import multilogger
from abc import ABCMeta,abstractmethod

# TODO: make these a property of the board, and rewrite fixed handicap handling
nine_star_points = ((3,7),(7,3),(3,3),(7,7),(5,5))
thirteen_star_points = ((4,4), (9,9), (4,9), (9,4), (7,7),(4,7),(9,7),(7,4),(7,9))
nineteen_star_points = ((4,4),(16,16),(4,16),(16,5),(10,10),(4,10),(16,10),(10,4),(16,4))

def score_japanese(player, territory):
	player.score = territory + player.captures + player.komi

class GoRules(object):
	'''Abstract base class for objects which handle game rules'''
	__metaclass__ = ABCMeta

	def __init__(self):
		object.__init__(self)
		self.testboard = None
		self._parameters = {}
		self.game = None
		self.errors = gameErrors.ErrorList() # List of rule violations encountered during a move

	def setup(self, game):
		'''Start game. Black goes first, unless there was a handicap'''
		self.game = game

		# TODO: loop through teams handling fixed handicap, go to next player if so
		game.start() # skip handicap placement

	@property
	def parameters(self):
		'''Game parameters which must be set to start the game. This does not include komi or handicap as these are properties of the team.'''
		return self._parameters.values()

	def parameter(self, name):
		'''Retrieve a game parameter by name'''
		return self._parameters[name]

	def fail(self):
		# Currently multiple errors aren't handled by the GUI which relies on exceptions to handle invalid moves etc. This is a temporary hack until I rewrite that.
		self.errors.check()

	def place_handicap(self, move):
		'''Handle manual placement of handicap stones in the same way as regular moves by default'''
		self.play_move(move)

	@abstractmethod
	def gameover(self):
		'''Return true if the game is over. If a winner is not set, the game will go into the MARK_DEAD state, and then the game will be scored.'''
		pass

	def more_handicap(self, player):
		'''Called after accepting a new handicap stone. Returns true if the player has more handicap stones to place.'''
		return False

	@abstractmethod
	def play_move(self, move):
		'''Handle a normal game move'''
		pass

	@abstractmethod
	def change_active_player(self):
		'''Change the active player on the current team after a move is played'''
		pass

	@abstractmethod
	def change_team(self):
		'''Change the team after a move is played'''
		pass

	@abstractmethod
	def score_player(self, player):
		'''Calculate the score of a player at the end of the game'''
		pass

	def check_suicide(self,position,board):
		'''check to see if the stone has any liberties'''
		group = board.group(position)
		if group.liberties == 0:
			self.errors.fail('SuicideError')

	def check_ko(self,move,board,history):
		'''Check to see if the move resets the board to any of its previous states'''
		if board in history:
			self.errors.fail('KoError')

	def begin(self):
		'''Start a transactional operation on the board'''
		self.testboard = copy(self.game.board)
	
	def rollback(self):
		'''Revert a transactional operation on the board'''
		self.testboard = None

	def commit(self):
		'''Commit a transactional operation on the board'''
		self.game.board = self.testboard
		self.testboard = None

	@property
	def board(self):
		if self.testboard is None:
			return self.game.board
		else:
			return self.testboard


class AGARules(GoRules):
	'''American go association rules'''

	def gameover(self):
		'''Returns true if the game is over, i.e. white then black passes consecutively. If a winner is not set, the game will go into the MARK_DEAD state, and then the game will be scored.'''
		history = self.game.moves
		return len(history) >= 2 \
			and history[-1].type == 'pass' \
			and history[-1].player == self.game.white \
			and history[-2].type == 'pass' \
			and history[-2].player == self.game.black

	def play_move(self, move):
		'''Handle a normal game move by the current player.'''
		self.errors.clear()
		self.begin()

		# Place the stone
		try:
			self.board.place_stone(move)
		except board.BoardError as error:
			self.errors.fail(error.__class__.__name__)
			self.rollback()
			return

		# Capture enemy stones
		move.player.captures += self.board.remove_dead_stones(move)

		self.check_suicide(move.position, self.board)
		self.check_ko(move, self.board, self.game.history)

		# Check for errors
		if self.errors:
			self.rollback()
		else:
			self.commit()

	def change_active_player(self):
		'''N/A - teams not implemented yet'''
		pass

	def change_team(self):
		'''Don't have teams yet; this changes player from black to white and vice versa'''
		if self.game.next_player == self.game.black:
			debug('white')
			self.game.next_player = self.game.white
		else:
			debug('black')
			self.game.next_player = self.game.black

	def score_player(self, player, territory):
		'''Calculate the score of a player at the end of the game'''
		return score_japanese(player, territory)

class FloatParameter(object):
	'''Represents a game parameter which must be a valid floating point number'''
	def __init__(self,name,value=None,range=None):
		self.name  = name
		self.value = None
		self.range = None
		self.pattern = re.compile('-?\d+')

	def validate(self):
		if self.value is None:
			return False

		if self.range is not None:
			return self.range[0] < self.value < self.range[1]

		return True

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
