#!/usr/bin/python
'''The classes in this module implement a Go board. Given a grid, the board lets you add and remove stones and group connected stones. There is no rule checking done by the board itself - this is taken care of in the rules module.

This module defines some constants which are used to distinguish the nature of the stones on the board:

	`board.STONE`
		Represents a live stone
	`board.DEAD_STONE`
		Represents a dead stone
'''
from copy import copy,deepcopy
from observer import Observable
from geometry import RectangularGrid
import multilogger

# Define constants used for describing the state of a board point.
# Grid values are either None (empty) or a tuple of (player, state)
STONE      = 0
DEAD_STONE = 1

# Define some exceptions
class BoardError(Exception):
	'''Exceptions thrown on invalid board operations.'''

class NonExistentPointError(BoardError):
	'''Exception thrown when trying to place a stone on a non existant point.'''
	pass

class OccupiedError(BoardError):
	'''Exception thrown when trying to place a stone on an occupied point.'''
	pass

class SizeError(BoardError):
	'''The size of the board is too big or small.'''
	pass


class Board(Observable):
	'''A rectangular board. Stones can be added to any square which isnt occupied. Each board object contains a grid of points, which are set to `None` if empty, otherwise contain a tuple of `(player,type)`, where type is either `board.STONE` or `board.DEAD_STONE`.'''

	def __init__(self,grid):
		Observable.__init__(self)
		self.grid = grid
		self.territory = {}

	def __eq__(self, other):
		'''Two boards are the same if all squares have the same state.'''
		return self.grid == other.grid

	def __copy__(self):
		'''Make a copy of this board.'''
		newgrid = copy(self.grid)
		newgrid.points = {}
		newgrid.connections = {}
		for i,j in self.grid.get_points():
			newgrid.points[i] = j
		for i,j in self.grid.get_connections():
			newgrid.connections[i] = j

		return Board(newgrid)

	def positions(self):
		'''Iterate over valid board coordinates.'''
		return self.grid.get_positions()

	def points(self):
		'''Iterator yielding tuples representing the coordinates of the points and their values.'''
		return self.grid.get_points()

	def connections(self):
		'''An iteratator over the connections of the grid, yielding tuples of two board points.'''
		return self.grid.get_connections()

	def place_stone(self, move):
		'''Attempt to place a stone at the given position. Throws an exception if there is not an empty space at that position.'''
		# Check that there is a free space at that position
		self.check_free_space(move)

		# Place the stone
		self.set_point(move.position, (move.player, STONE))

	def check_free_space(self,move):
		'''Check to see if the space exists and is empty.'''
		if not self.is_empty(move.position):
			raise OccupiedError

	def remove_stone(self, pos):
		'''Remove a stone from the board.'''
		if self.is_empty(pos):
				raise BoardError('Tried to remove a stone that doesn\'t exist')

		self.set_point(pos, None)

	def get_territory(self, pos):
		'''Return the owner of the territory at position `pos`, or `None` if it is neutral.'''
		if pos in self.territory:
			return self.territory[pos]

	def count_territory(self):
		'''Return a dictionary containing the points of territory for each player. Assumes the territory has been calculated already.'''
		result = {}
		for pos,player in self.territory.iteritems():
			if player is not None:
				if player not in result:
					result[player] = 1
				else:
					result[player] += 1
		return result

	def set_territory(self, pos, player=None):
		'''Mark a particular point as belong to a player.'''
		self.territory[pos] = player

	def reset_territory(self):
		'''Reset previously calculated territories.'''
		self.territory = {}

	def get_point(self, pos):
		'''Get the value of a board point.'''
		try:
			point = self.grid.get_point(pos[0], pos[1])
		except:
			raise NonExistentPointError
		return point

	def set_point(self, pos, value):
		'''Set the value of a board point.'''
		try:
			self.grid.set_point(pos[0],pos[1],value)
		except:
			raise NonExistentPointError

	def is_empty(self, pos):
		'''Check if a point is empty.'''
		point = self.get_point(pos)
		if point is None:
			return True
		return (point[1] != STONE)

	def neighbours(self,pos):
		'''Returns a list of positions of the neighbouring points.'''
		return self.grid.neighbours(pos[0], pos[1])[::]

	def remove_dead_stones(self,move):
		'''Remove any stones which are captured by this move.'''
		captures = 0
		already_checked = set()
		for position in self.neighbours(move.position):
			if (position not in already_checked) and not self.is_empty(position) and (self.get_point(position)[0] is not move.player):

				# Start a new group
				group = Group(self,position)

				# Save the positions of all the stones in this group to avoid checking the same group multiple times
				already_checked |= group.stones

				if not group.liberties: # the group is captured!

					# Update the number of captured stones for this player
					captures += len(group.stones)
					group.kill() # remove the stones from the board
		return captures

	def size(self):
		'''Return the size of the board.'''
		return self.grid.size()

	def group(self,position):
		'''Return the group of stones at a given position.'''
		debug(position)
		return Group(self,position)

	def mark_territory(self):
		'''Find empty space surrounded by a single player, and mark it as that player's territory. Assumes all stones are live unless marked otherwise.'''
		self.reset_territory()
		done = [] # points which have been checked already

		# Look for areas of empty spaces
		for pos in self.positions():

			if not self.is_empty(pos):
				continue

			# Mark already checked points
			if pos in done:
				continue
			else:
				done.append(pos)

			surroundingPlayer = None
			area = [pos]

			# Make a stack of unchecked points in the area
			unchecked = self.neighbours(pos)

			# Grow the area until we reach the border.
			# If it touches no players or >1 players it's neutral
			# Otherwise, mark it as the surrounding player's territory
			while True:

				# If we've checked all the points in this area, continue looking for more areas
				if not unchecked:
					if surroundingPlayer is not None:
						for pos in area:
							self.set_territory(pos,surroundingPlayer)
					break
	
				nextPos = unchecked.pop()

				if nextPos in area:
					continue

				if not self.is_empty(nextPos):
					player,state = self.get_point(nextPos)
					if surroundingPlayer is not None and surroundingPlayer is not player:
						break
					elif surroundingPlayer is None:
						surroundingPlayer = player
				else:
					area.append(nextPos)
					done.append(nextPos)
					unchecked.extend(self.neighbours(nextPos))

	def toggle_dead(self,position):
		'''Toggles whether a group is marked dead or not. Assumes that territory is marked before this method is called, but markings are not guarenteed to be correct afterwards. It would not make sense to have dead stones in your own territory, so we treat any groups that are only seperated by the player's territory as linked here.'''

		here = self.get_point(position)
		if here is None:
			return

		player,state = here
		if state == STONE:
			new_state = DEAD_STONE
		elif state == DEAD_STONE:
			new_state = STONE
		else:
			return

		self.set_point(position, (player, new_state))

		neighbours = self.neighbours(position)
		stones = []
		checked = []

		while True:
			if not neighbours:
				break

			next = neighbours.pop()

			# Don't check the same point twice
			if next in checked:
				continue
			if next in stones:
				continue
			checked.append(next)

			# Empty space signifies the border of the group
			if self.get_point(next) is None:

				# Player territory is ok
				if self.get_territory(next) is player:
					neighbours.extend(self.neighbours(next))
				continue

			owner,state = self.get_point(next)
			if owner is player:
				neighbours.extend(self.neighbours(next))

				if state in (STONE, DEAD_STONE):
					self.set_point(next,(player, new_state))


class Group:
	'''A group of stones which are connected.'''
	def __init__(self,board,position):
		self.stones = set() # list of positions of the stones
		self.liberties = False
		self.board = board
		debug('using point '+str(position))
		start_point = board.get_point(position)
		if start_point is not None:
			self.owner = start_point[0]
			self.stones.add(position)
			self.find_connected_stones(position)

	def __eq__(self,other):
		if len(self.stones) is not len(other.stones) or self.owner is not other.owner or self.board is not other.board:
			return False

		# Check all the stones are the same
		for i in self.stones:
			if i not in other.stones:
				return False
		return True

	def find_connected_stones(self,position):
		'''Recursively add stones which are connected to the starting stone, and check for liberties.'''
		neighbours = self.board.neighbours(position)
		for next in neighbours:
			if next not in self.stones:
				if self.board.is_empty(next):
					self.liberties = True
				elif self.board.get_point(next)[0] is self.owner:
					self.stones.add(next)
					self.find_connected_stones(next)

	def kill(self):
		'''Remove the group from the board.'''
		for position in self.stones:
			debug('removed %s' % str(position))
			self.board.remove_stone(position)


class RectangularBoard(Board):
	'''Convenience class for creating regular rectangular boards.'''

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
		'''Number of points wide/tall the board is. This doesn't really have any use and is just intended for testing.'''
		x1,y1,x2,y2 = self.grid.size()
		return (x2-x1+1,y2-y1+1)

# Get a logger for this module
debug,info,warning,error = multilogger.logFunctions(__name__)
