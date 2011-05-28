#!/usr/bin/python
'''This module implements various rulesets which can be used to validate moves and score the game.'''
from copy import copy
import re
import gameErrors
import game
import board
import multilogger
from abc import ABCMeta,abstractmethod
from itertools import cycle

# TODO: make these a property of the board, and rewrite fixed handicap handling
nine_star_points = ((3,7),(7,3),(3,3),(7,7),(5,5))
thirteen_star_points = ((4,4), (9,9), (4,9), (9,4), (7,7),(4,7),(9,7),(7,4),(7,9))
nineteen_star_points = ((4,4),(16,16),(4,16),(16,5),(10,10),(4,10),(16,10),(10,4),(16,4))

def score_japanese(player):
	player.score = len(player.territory) + player.captures + player.komi

#TODO: provide means to serialize a rules object (i.e. their parameters and class/script file) for saving to file and hosting network games
class GoRules(object):
	'''Abstract base class for objects which handle game rules.'''
	__metaclass__ = ABCMeta

	def __init__(self):
		object.__init__(self)
		self._parameters = {}
		self.errors = gameErrors.ErrorList() # List of rule violations encountered during a move

	def setup(self, game):
		'''Called at the beginning of the game. Handles things like fixed handicap and komi, and who goes first. Normally black goes first, unless there was a handicap.'''
		# TODO: loop through teams handling fixed handicap, go to next player if so
		pass

	@property
	def parameters(self):
		'''Game parameters which must be set to start a game. This does not include komi or handicap as these are properties of the team.'''
		return self._parameters.values()

	def parameter(self, name):
		'''Retrieve a game parameter by name'''
		return self._parameters[name]

	def valid(self):
		'''True if all the parameters are valid (required to start a game).'''
		return all(map(RuleParameter.Valid,self.parameters))

	def place_handicap(self, game, move):
		'''Place a handicap stone. We handle this in the same way as regular moves by default.'''
		self.play_move(move)

	@abstractmethod
	def gameover(self):
		'''Return true if the game is over. If a winner is not set, players will be able to mark dead stones before the game is scored.'''
		pass

	def more_handicap(self, game, player):
		'''Called after accepting a new handicap stone. Returns true if the player has more handicap stones to place.'''
		return False

	@abstractmethod
	def play_move(self, game, move):
		'''Handle a normal game move.'''
		pass

	@abstractmethod
	def change_active_player(self, game):
		'''Change the active player on the current team after a move is played.'''
		pass

	@abstractmethod
	def change_team(self, game):
		'''Change the team after a move is played.'''
		pass

	@abstractmethod
	def score_player(self, player):
		'''Calculate the score of a player at the end of the game.'''
		pass

	def check_suicide(self,position,board):
		'''Check to see if the stone has any liberties.'''
		group = board.group(position)
		if not group.liberties:
			self.errors.fail('SuicideError')

	def check_ko(self,move,board,history):
		'''Check to see if the move resets the board to any of its previous states.'''
		if board in history:
			self.errors.fail('KoError')


class AGARules(GoRules):
	'''American go association rules'''

	def gameover(self, game):
		'''Returns true if the game is over, i.e. white then black passes consecutively. If a winner is not set, the game will go into the MARK_DEAD state, and then the game will be scored.'''
		history = game.moves
		return len(history) >= 2 \
			and history[-1].type == 'pass' \
			and history[-2].type == 'pass' \
			and history[-2].player.team == 'black'

	def play_move(self, game, move):
		'''Handle a normal game move by the current player.'''
		self.errors.clear()
		game.begin()

		# Place the stone
		try:
			game.board.place_stone(move)
		except board.BoardError as error:
			self.errors.fail(error.__class__.__name__)
			game.rollback()
			return

		# Capture enemy stones
		move.player.captures += game.board.remove_dead_stones(move)

		self.check_suicide(move.position, game.board)
		self.check_ko(move, game.board, game.history)

		# Check for errors
		if self.errors:
			game.rollback()
		else:
			game.commit()

	def change_active_player(self, game):
		'''N/A - teams not implemented yet'''
		pass

	def change_team(self, game):
		'''Don't have teams yet; this changes player from black to white and vice versa'''
		current = game.next_player
		players = cycle(game.active_players)
		p = None
		while p is not current:
			p = players.next()
		game.next_player = players.next()

	def score_player(self, player):
		'''Calculate the score of a player at the end of the game'''
		return score_japanese(player)


class RuleParameter(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def valid(self):
		pass

class FloatParameter(RuleParameter):
	'''Represents a game parameter which must be a valid floating point number'''
	def __init__(self,name,value=None,range=None):
		self.name  = name
		self.value = None
		self.range = None
		self.pattern = re.compile('-?\d+')

	def valid(self):
		if self.value is None:
			return False

		if self.range is not None:
			return self.range[0] < self.value < self.range[1]

		return True

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
