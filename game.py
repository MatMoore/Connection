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
import player
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

	def __init__(self,board,players=(),fixed_handicap=0,komi=0,custom_handicap=0,ruleset=None):

		Observable.__init__(self)
		self._board = board
		self._testboard = None

		if ruleset:
			self.ruleset = ruleset
		else:
			self.ruleset = rules.AGARules()

		self.history = [] # the board at all times in the past
		self.moves = [] # the list of moves

		if not players:
			black_player = player.PlayerSettings('black','Black')
			white_player = player.PlayerSettings('black','Black',komi=komi)
			players = [player.Player(p, self) for p in (black_player, white_player)]
		else:
			for p in players:
				p.game = self

		self.players = players

		self.next_player = self.players[0]
		self.winner = None
		self.state = PLACE_HANDICAP

		# Handle handicap, komi etc
		self.ruleset.setup(self)

		# If manual handicap stones need to be placed, change to that team;
		# otherwise, begin the game
		if not self.skip_completed_handicap():
			self.start()

	def start(self):
		'''Start the game. All stones placed will henceforth be treated as regular moves and not handicap stones.'''
		info('Starting game')
		self.state = PLAY_GAME

	def end(self):
		if self.state != MARK_DEAD and self.winner is None:
			self.state = MARK_DEAD
		else:
			self.state = GAME_OVER

	@property
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
			self.ruleset.play_move(self, move)
		elif self.state == PLACE_HANDICAP:
			self.ruleset.place_handicap(move)

		# Raise an exception if the move was invalid
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
		if self.ruleset.gameover(self):
			self.end()
		else:
			# Change the active player of the current team
			self.ruleset.change_active_player(self)

			# Now it is the next team's turn
			self.ruleset.change_team(self)

	def end_place_handicap(self):
		'''Check if handicap placement is complete and handle changing players'''
		debug('end_place_handicap')

		# Change the active player of the current team
		self.ruleset.change_active_player(self)

		# If everyone is done placing handicaps, the next team begins the game
		if not self.skip_completed_handicap():
			self.ruleset.change_team(self)
			self.start()

	def skip_completed_handicap(self):
		'''Change to the next team/player that has handicap stones to place. Returns false if there are none.'''
		info('Waiting for handicap to be placed')

		if not self.more_handicap():
			return False

		while not self.ruleset.more_handicap(self, self.next_player):
			# Keep changing teams until one has handicap to place
			self.ruleset.change_team(self)
		return True

	def more_handicap(self):
		'''Check if there are any more handicap stones to be placed.'''
		return any([self.ruleset.more_handicap(self, player) for player in self.active_players])

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
		move = SpecialMove('resign',self.next_player)
		self.next_player.resign()

		if len(self.active_players) > 1:
			return

		if self.state in (GAME_OVER, MARK_DEAD):
			raise GameOverError

		self.winner = self.active_players[0]

		self.moves.append(move)
		self.end()
		self.notify(move)

	def player_territory(self, player):
		'''The territory belonging to a player'''
		return self.board.player_territory(player)

	def score_player(self, player):
		'''The score for a player'''
		return self.ruleset.score_player(player)

	def score(self):
		'''Score the game.'''
		debug('Scoring')
		self.board.mark_territory()

		self.winner = max(self.players, key=self.score_player)

		debug('ending')
		self.end()
		self.notify(None)

	@property
	def active_players(self):
		'''A list of players who haven't resigned'''
		return filter(lambda p: not p.resigned, self.players)

	@property
	def state(self):
		'''Integer representing the current game stage.'''
		return self._game_state

	def begin(self):
		'''Start a transactional operation on the board'''
		self._testboard = copy(self._board)
	
	def rollback(self):
		'''Revert a transactional operation on the board'''
		self._testboard = None

	def commit(self):
		'''Commit a transactional operation on the board'''
		self._board = self._testboard
		self._testboard = None

	@property
	def board(self):
		if self._testboard is None:
			return self._board
		else:
			return self._testboard


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
		return '%s %s%d'%(self.player.team,x,y)

class SpecialMove:
	'''Represents a pass/resign move.'''
	def __init__(self,type,player):
		self.type = type
		self.player = player
		self.position = (-1,-1)

	def __str__(self):
		return '%s %s'%(self.player.team,self.type)

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
