#!/usr/bin/python
'''This module implements various rulesets which can be used to validate moves and score the game.'''
from copy import copy
from board import Group

# Invalid move exceptions
class InvalidMove(Exception): pass
class SuicideError(InvalidMove): pass
class KoError(InvalidMove): pass
class NonExistantSquareError(InvalidMove): pass

nine_star_points = ((3,7),(7,3),(3,3),(7,7),(5,5))
thirteen_star_points = ((4,4), (9,9), (4,9), (9,4), (7,7),(4,7),(9,7),(7,4),(7,9))
nineteen_star_points = ((4,4),(16,16),(4,16),(16,5),(10,10),(4,10),(16,10),(10,4),(16,4))

class AGARules:
	'''American go association rules'''
	#check if a move on the board
	def check_suicide(self,move,board):
		'''check to see if the stone has any liberties'''
		group = board.group(move.position)
		if group.liberties == 0:
			raise SuicideError

	def check_ko(self,move,board,history):
		'''Check to see if the move resets the board to any of its previous states'''
		if board in history:
			raise KoError

	def check_rules(self,move,board,history):
		testboard = copy(board)
		testboard.place_stone(move) #try the move
		testboard.remove_dead_stones(move) #remove stones it captures
		self.check_suicide(move,testboard) #check the stone is alive
		self.check_ko(move,testboard,history) #check it doesnt repeat a previous board position

	def game_over(self,history,white,black):
		'''game is over when black passes, then white passes'''
		return len(history) >= 2 \
			and history[-1].type == 'pass' \
			and history[-1].player == white \
			and history[-2].type == 'pass' \
			and history[-2].player == black

	def score(self, board, black, white, komi):
		return score_japanese(board, black, white, komi)

# TODO: rewrite this to check the board type or something
# it should only place stones for the standard boards
#		def place_handicap(self,number,board,black):
#				if boardsize == (9,9):
#						stars = AGARuleset.nine_star_points
#				elif boardsize == (13,13):
#						stars = AGARuleset.thirteen_star_points
#				elif boardsize == (19,19):
#						stars = AGARuleset.nineteen_star_points

#				spaces = len(stars)
#				if fixed_handicap > spaces:
#						fixed_handicap = spaces
#				for i in range(fixed_handicap):
#						board.place_stone(stars[i],black)
#
#				return spaces

def score_japanese(board, black, white, komi):
	board.mark_territory()
	territory = board.count_territory()
	for player in (black,white):
		if player not in territory:
			territory[player] = 0

		player.score = territory[player] + player.captures

	white.score += komi
