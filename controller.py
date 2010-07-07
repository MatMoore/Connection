'''Objects which control making moves in a ggame'''
from observer import Observable
import game

class Controller(Observable):
	'''Object which keeps track of the current player and makes moves for the current player. Display objects should observe this to work out whether or not to accept moves'''
	def __init__(self):
		Observable.__init__(self)
		self.local_players = []
		self.remote_players = []
		self.accept_local_moves = False
		self.game = None

	# maybe take player params and return the player object instead?
	def add_local_player(self, team, name):
		player = game.Player(team, name)
		self.local_players.append(player)
		return player

	def add_remote_player(self, team, name):
		pass

	def begin_game(self,board,fixed_handicap=0,komi=0,custom_handicap=0,ruleset=None):
		black_player = None
		white_player = None

		for i in (self.local_players + self.remote_players):
			if i.color == 'black':
				black_player = i
				print 'Black player is %s' % i.name
			elif i.color == 'white':
				white_player = i
				print 'White player is %s' % i.name

		self.game = game.TwoPlayerGame(board,black_player,white_player,fixed_handicap,komi,custom_handicap,ruleset)
		self.game.register_listener(self.on_move)
		self.on_move() # Needed to get the first "next player"
		# TODO notify remote players

	def on_move(self, *args):
		player = self.game.next_player
		if player in self.local_players:
			self.accept_local_moves = True
			print 'accepting local moves'
		else:
			print 'not accepting local moves'
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
		if player in self.local_players:
			self.game.pass_turn()
			#TODO fix game to accept player for the pass/resign functions

	def resign(self):
		if self.game is None:
			return
		if player in self.local_players:
			self.game.resign()

class GTPPlayer(object):
	pass
