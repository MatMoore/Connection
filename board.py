from copy import copy,deepcopy
from observer import Observable
from geometry import RectangularGrid

class BoardError(Exception):
	'''Exceptions thrown on invalid board operations'''

class NonExistantPointError(BoardError):
	'''Exception thrown when trying to place a stone on a non existant point'''
	pass

class OccupiedError(BoardError):
	'''Exception thrown when trying to place a stone on an occupied point'''
	pass

class SizeError(BoardError):
	'''The size of the board is too big or small'''
	pass

class Board(Observable):
	'''A rectangular board. Stones can be added to any square which isnt occupied.'''

	def __init__(self,grid):
		Observable.__init__(self)
		self.grid = grid

	def __eq__(self, other):
		'''Two boards are the same if all squares have the same state'''
		return self.grid == other.grid

	def __copy__(self):
		'''Make a copy of this board.'''
		return Board(deepcopy(self.grid))

	def points(self):
		'''Iterator yielding tuples representing the coordinates of the points and their values'''
		return self.grid.get_points()

	def connections(self):
		'''Iterate over the connections of the grid'''
		return self.grid.get_connections()

	def place_stone(self, move):
		'''Attempt to place a stone at the given position. Throws an exception if there is not an empty space at that position'''
		#check that there is a free space at that position
		self.check_free_space(move)

		#place the stone
		self.grid.set_point(move.position[0], move.position[1], move.player)

	def check_free_space(self,move):
		'''Check to see if the space exists and is empty'''
		try:
			if self.grid.get_point(move.position[0], move.position[1]) != None:
				raise OccupiedError
		except:
			raise NonExistantPointError

	def remove_stone(self, pos):
		if not is_empty(self,pos):
				raise OccupiedError

		self.grid.set_point(pos[0], pos[1], None)

	def get_point(self, pos):
		try:
			point = self.grid.get_point(pos[0], pos[1])
		except:
			raise NonExistantPointError
		return point

	def is_empty(self, pos):
		return (self.get_point(pos) is None)

	def neighbours(self,pos):
		'''Returns a list of positions of the neighbouring squares'''
		return self.grid.neighbours(pos[0], pos[1])

	def remove_dead_stones(self,move):
		'''Remove any stones which are captured by this move'''
		already_checked = []
		for position in self.neighbours(move.position):
			if (position not in already_checked) and (self.get_point(position) is not move.player):

				# Start a new group
				group = Group(self,position)

				# Save the positions of all the stones in this group to avoid checking the same group multiple times
				already_checked.extend(group.stones)

				if group.liberties == 0: #the group is captured!

					# Update the number of captured stones for this player
					move.player.captures += len(group.stones)
					group.kill() #remove the stones from the board

	def size(self):
		return self.grid.size()

class Group:
	'''A group of stones which are connected'''
	def __init__(self,board,position):
		self.stones = [] #list of positions of the stones
		self.liberties = 0
		self.board = board
		start_point = board.get_point(position)
		if start_point is not None:
			self.owner = start_point
			self.stones.append(position)
			self.find_connected_stones(position)

	def __eq__(self,other):
		#check the size, liberties and board is the same
		if len(self.stones) is not len(other.stones) or self.owner is not other.owner or self.board is not other.board:
			return False

		#check all the stones are the same
		for i in self.stones:
			if i not in other.stones:
				return False
		return True

	def find_connected_stones(self,position):
		'''Recursively add stones which are connected to the starting stone, and count the liberties of the group.'''
		neighbours = self.board.neighbours(position)
		for next in neighbours:
			if next not in self.stones:
				if self.board.is_empty(next):
					self.liberties += 1
				elif self.board.get_point(next) is self.owner:
					self.stones.append(next)
					self.find_connected_stones(next)

	def kill(self):
		for position in self.stones:
			self.board.remove_stone(position)

class RectangularBoard(Board):
	'''Class for creating rectangular boards'''
	def __init__(self, size):
		try:
			x,y = size
		except:
			raise SizeError()
		if x < 3 or x > 50:
			raise SizeError()
		if y < 3 or y > 50:
			raise SizeError()

		grid = RectangularGrid(x, y)
		Board.__init__(self,grid)

	def get_size(self):
		'''Number of points wide/tall the board is. This doesn't really have any use and is just intended for testing'''
		x1,y1,x2,y2 = self.grid.size()
		return (x2-x1+1,y2-y1+1)
