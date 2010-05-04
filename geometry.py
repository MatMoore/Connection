'''Classes for modelling the goboard itself, i.e. an arrangement of points with lines connecting them. No game logic is included.

There are two types of object here -

Grid = A collection of points which we can set to arbitary values. The interface should allow us to get/set the value of a point by its coordinates, iterate over the points, and retrieve the points connected to any given point, as well as compare two grids.

Currently Grids are limited to 2 dimensional regular structures, but a more generic class may be created in the future to facilitate more exotic go boards.

Lattice = convienceince classes for feeding to a grid in order to produce crystal-like structures that look identical at each of the lattice points.

NB: Grid/lattice coordinates should all be integers. They are not intended to convey scale, only the relative position of points.
'''
# TODO:
# Allow for many exotic board types...
# 2D: rectangular, cylindrical, mobius, torus, hexagonal, triangular, combinations,
# 3D: diamond, cubic
# 4D: ???
from itertools import izip
import sys
from observer import Observable

class Grid(Observable):
	'''A representation of a 2D grid with each point holding some value.
	Stores the relative location of each point and the lines connecting them.
	Lattice is a list of points representing the lattice structure the grid is based around.
	Basis is a tuple of coordinates of the grid points relative to the lattice points.
	Connections is a list of 4-tuples of the form (x1,y1,x2,y2) indicating how points in the basis are connected'''

	def __init__(self, lattice, basis, connections, default_value=None):
		'''Store points and connections'''
		Observable.__init__(self)
		self.points = {}
		self.connections = {}
		self.xmax = -1000
		self.ymax = -1000
		self.xmin = 1000
		self.ymin = 1000

		for lx,ly in lattice.items():

			#Add the points by superimposing the basis onto each lattice point
			for b in basis:
				bx, by = b
				self.points[(lx+bx, ly+by)] = default_value
				self.connections[(lx+bx, ly+by)] = []

				self.xmin = min(self.xmin, lx+bx)
				self.ymin = min(self.ymin, ly+by)
				self.ymax = max(self.ymax, ly+by)
				self.xmax = max(self.xmax, lx+bx)

		#now connect the points
		for lx,ly in lattice.items():

			try:
				for c in connections:
					cx1, cy1, cx2, cy2 = c
					a = (lx+cx1, ly+cy1)
					b = (lx+cx2, ly+cy2)
					if a in self.points and b in self.points:
						self.connections[a].append(b)
						self.connections[b].append(a)
#					else:
						#print 'Missing points for connection '+str(a)+'-'+str(b)
						#if a not in self.points: print a
						#if b not in self.points: print b
			except KeyError:
				raise Exception('Invalid connections')

	def __eq__(self, other):
		return (self.points == other.points and self.connections == other.connections)

	def __len__(self):
		return len(self.points)

	def neighbours(self, x, y):
		try:
			return self.connections[(x,y)]
		except KeyError:
			raise Exception('Bad grid coordinates')

	def set_point(self, x, y, val):
		try:
			self.points[(x,y)] = val
			self.notify() #notify observers on changes
		except KeyError:
			raise Exception('Bad grid coordinates')

	def get_point(self, x, y):
		try:
			return self.points[(x,y)]
		except KeyError:
			print 'bad point ' + str(x) +','+str(y)
			raise Exception('Bad grid coordinates')

	def get_points(self):
		return self.points.iteritems()

	def get_connections(self):
		return self.connections.iteritems()

	def size(self):
		return self.xmin,self.ymin,self.xmax,self.ymax

class RectangularGrid(Grid):
	'''A rectangular grid. Aspect ratio should be a natural number (horizontal spacing >= vertical spacing)'''

	def __init__(self, width, height, aspect_ratio=1):
		aspect_ratio = int(aspect_ratio) #no floats please!
		lattice = RectangularLattice(width, height, aspect_ratio)
		basis = ((0, 0),)
		connections = ((0, 0, 1*aspect_ratio, 0), (0, 0, 0, 1))
		Grid.__init__(self, lattice, basis, connections)

class FoldedGrid(RectangularGrid):
	'''A rectangular grid where sides connect with each other.
	Joins is a list of tuples indicating which sides are joined, where each of the two values can be N, E, S or W
	Reverse_joins is the same except there is also a twist, so one side can map to another side reversed (or the same side)'''

	def __init__(self, width, height, aspect_ratio, joins = [], reverse_joins = []):
		RectangularGrid.__init__(self, width, height, aspect_ratio)

		#Lists of coordinates making up each side
		east = []
		west = []
		north = []
		south = []


		#East/West coordinates
		x1 = 0
		x2 = (width - 1) * aspect_ratio
		for i in range(height):
			east.append((x1, i))
			west.append((x2, i))

		#North/South coordinates
		y1 = 0
		y2 = height - 1
		for i in range(width):
			i *= aspect_ratio
			north.append((i, y1))
			south.append((i, y2))

		sides = {'E':east, 'W':west, 'N':north, 'S':south}

		#Make the extra connections
		try:
			for sideA, sideB in joins:
				#Zip the two sides together to get a tuple of tuples (coordinates) for each connected pair
				for c1, c2 in izip(sides[sideA], sides[sideB]):
					self.connections[c1].append(c2)
					self.connections[c2].append(c1)

			for sideA, sideB in reverse_joins:
				#This time the second side is reversed!
				for c1, c2 in izip(sides[sideA], reversed(sides[sideB])):
					#print str(c1) + '-' + str(c2)
					self.connections[c1].append(c2)
					self.connections[c2].append(c1)

		except KeyError:
			raise Exception('Invalid value for join or reverse_join')


class RectangularLattice:
	'''List of coordinates of points arranged in a grid'''

	def __init__(self, width, height, aspect_ratio=1):
		aspect_ratio = int(aspect_ratio) #no floats please
		self.points = []
		for i in range(width):
			i *= aspect_ratio
			for j in range(height):
				self.points.append((i,j))

	def items(self):
		for i in self.points:
			yield i
