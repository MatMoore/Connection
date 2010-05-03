#!/usr/bin/python
'''The game logic for a two player game of go'''
#TODO: modify game to take players as args
from observer import Observable
from copy import copy
import string
import rules
import geometry

# Define some exceptions
class GameError: pass

class NotYourTurnError(GameError):
	'''Thrown when a player makes a move when it's not their turn'''
	pass

class TwoPlayerGame(Observable):
		'''Handles all the game logic for a 2 player game of go.'''

		def __init__(self,board,fixed_handicap=0,komi=0,black='Black',white='White',custom_handicap=0,ruleset=None):
				Observable.__init__(self)
				self.board = board

				if ruleset:
						self.ruleset = ruleset
				else:
						self.ruleset = rules.AGARules()

				self.history = [] # the board at all times in the past
				self.moves = [] #the list of moves
				self.black = Player('black',black)
				self.white = Player('white',white)
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

				#black goes first, unless they have a handicap
				if self.handicap and self.remaining_handicap == 0:
						self.next_player = self.white
				else:
						self.next_player = self.black

				#extra points to compensate white for black going first
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

		def last_move(self):
				if self.moves:
						return self.moves[-1]

		def play_move(self,position,player):
				'''Play the next move'''
				if player is not self.next_player:
						raise NotYourTurnError

				move = Move(position, player)

				#check the move doesn't break the rules (will raise an exception if it does)
				self.ruleset.check_rules(move,self.board,self.history)

				#play the move
				self.board.place_stone(move)
				self.board.remove_dead_stones(move)

				#save the board state and move for later
				self.moves.append(move)
				self.history.append(copy(self.board))

				if not self.remaining_handicap:
						self.change_player()
				else:
						self.remaining_handicap -= 1

				self.notify()

		def pass_turn(self):
				'''Pass turn. If both players pass the game is over.'''
				self.moves.append(SpecialMove('pass',self.next_player))
				self.change_player()
				self.notify()

		def resign(self):
				if self.next_player == self.black:
						self.winner = self.white
				else:
						self.winner = self.black

				self.notify()

		def game_over(self):
				return self.winner is not None

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
		self.position = position
		self.player = player

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
