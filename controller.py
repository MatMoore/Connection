'''Object which manages the different players in the game and keeps track of when we should accept moves from the local client.

General usage:

1. Add players with add_local_player and add_remote_player, then call begin_game.

2. Local players play moves using play_move, pass_turn and resign. This will make the move for the appropriate player. The object will notify when it is one of the local players' turns.

3. Remote players play moves through the game object directly. The remote player object should also listen for and relay the local moves.

4. After each move the game object should notify it's listeners, at which point they can check whether the game state has changed.

5. When the game state is MARK_DEAD, stones can be marked dead using toggle_dead, and confirmed using confirm_dead, for both local and remote players. Once all players have confirmed, the game will end.
'''
from observer import Observable
import game
import multilogger

class Controller(Observable):
	'''Object which keeps track of the players and makes moves for the current player. Display objects should observe this to work out whether or not to accept moves.'''
	def __init__(self):
		Observable.__init__(self)
		self.local_players = []
		self.remote_players = []
		self.accept_local_moves = False
		self.game = None
		self.confirmed_dead_stones_remote = set()
		self.confirmed_dead_stones = False

	def add_local_player(self, team, name):
		'''Add a local player to the game'''
		player = game.Player(team, name)
		self.local_players.append(player)
		return player

	def add_remote_player(self, team, name):
		'''Add a remote player to the game'''
		pass

	def toggle_dead(self, pos):
		self.confirmed_dead_stones_remote = set()
		self.confirmed_dead_stones = False
		self.game.board.toggle_dead(pos)

	def confirm_dead(self, local=True, player=None):
		if player is not None and not local:
			debug('Confirmed dead stones for '+player.name)
			self.confirmed_dead_stones_remote.add(player)
		elif not local:
			raise Exception('confirm_dead called without player')
		else:
			debug('Confirmed dead stones for local players')
			self.confirmed_dead_stones = True

		if self.confirmed_dead_stones and self.confirmed_dead_stones_remote == set(self.remote_players):
			self.game.score()

	# TODO: check we have the correct number of players before starting the game
	def begin_game(self,board,fixed_handicap=0,komi=0,custom_handicap=0,ruleset=None):
		'''Create a game between the current players'''
		black_player = None
		white_player = None

		for i in (self.local_players + self.remote_players):
			if i.color == 'black':
				black_player = i
				info('Black player is "%s"' % i.name)
			elif i.color == 'white':
				white_player = i
				info('White player is "%s"' % i.name)

		self.game = game.TwoPlayerGame(board,black_player,white_player,fixed_handicap,komi,custom_handicap,ruleset)
		self.game.register_listener(self.on_move)
		self.on_move() # Needed to get the first "next player"

	def on_move(self, *args):
		'''Callback function called whenever a move is played'''
		player = self.game.next_player
		if player in self.local_players and self.game.state == game.PLAY_GAME:
			self.accept_local_moves = True
			debug('accepting local moves')
		else:
			debug('not accepting local moves')
			self.accept_local_moves = False
		self.notify(self.accept_local_moves,player)

	def play_move(self, position):
		if self.game is None:
			return
		player = self.game.next_player
		if player in self.local_players:
			self.game.play_move(position,player)

	def pass_turn(self):
		if self.game is None:
			return
		player = self.game.next_player
		if player in self.local_players:
			debug('Pass')
			self.game.pass_turn()
			# TODO fix game to accept player for the pass/resign functions

	def resign(self):
		if self.game is None:
			return
		player = self.game.next_player
		if player in self.local_players:
			debug('Resign')
			self.game.resign()

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
