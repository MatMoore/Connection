from game import *
from gtpplayer import *
import wx,os

imagedir = 'images'

class BoardImage(wx.Panel):
        def __init__(self,game,parent=None,id=wx.ID_ANY,humanPlayers=()):
                wx.Panel.__init__(self,parent,id,size=(360,360))
                game.board.attach(self) #listen for changes on the board
                smallboard = os.path.join(imagedir,'goboard9.jpg')
                whitestone = os.path.join(imagedir,'whitestone.png')
                blackstone = os.path.join(imagedir,'blackstone.png')
                self.background = wx.Bitmap(smallboard)
                self.black = wx.Bitmap(blackstone)
                self.white = wx.Bitmap(whitestone)
                self.Bind(wx.EVT_PAINT,self.OnPaint)
                self.Bind(wx.EVT_LEFT_DOWN,self.OnClick)
                self.Bind(wx.EVT_MOTION,self.OnMouseMove)
                self.Bind(wx.EVT_LEAVE_WINDOW,self.OnLeaveWindow)
                self.Bind(wx.EVT_SIZE, self.OnSize)
                self.game = game
                self.width = 40 #distance between points
                self.offset = 20 #distance between the first line and the edge of the board
                self.boardsize = 360 #width/height of board
                self.selectedPoint = None #the point the mouse is hovering over
                self.OnSize(None)
                self.players = humanPlayers

        def nearestPoint(self,pos):
                if pos[0] in range(self.boardsize) and pos[1] in range(self.boardsize):
                        nearestX = round(float(pos[0]-self.offset) / self.width) + 1
                        nearestY = round(float(pos[1]-self.offset) / self.width) + 1
                        if nearestX > 9:
                                nearestX = 9
                        elif nearestX < 1:
                                nearestX = 1
                        if nearestY > 9:
                                nearestY = 9
                        elif nearestY < 1:
                                nearestY = 1
                        return (nearestX,nearestY)

        def draw(self,dc):
          '''This handles all the drawing'''
          #draw the board
          dc.DrawBitmap(self.background,0,0)
          
          #draw the stones
          for pos,square in self.game.board.squares.items():
              if not square.empty():
                  x = self.offset + self.width*(pos[0]-1) - self.width/2.0
                  y = self.offset + self.width*(pos[1]-1) - self.width/2.0
                  player = square.owner.color
                  if player == 'black':
                      dc.DrawBitmap(self.black,x,y)
                  elif player == 'white':
                      dc.DrawBitmap(self.white,x,y)
          
          #draw the stone the player is placing            
          if self.selectedPoint and self.game.board.squares[self.selectedPoint].empty():
              x = self.offset + self.width*(self.selectedPoint[0]-1) - self.width/2.0
              y = self.offset + self.width*(self.selectedPoint[1]-1) - self.width/2.0
              player = self.game.current_player()
              if player == 'black' and player in self.players:
                  dc.DrawBitmap(self.black,x,y)
              elif player == 'white' and player in self.players:
                  dc.DrawBitmap(self.white,x,y)

        def update(self,object): #called when the board changes
                '''redraw the entire board'''
                self.updateDrawing(); #update buffer
                self.GetEventHandler().ProcessEvent(wx.PaintEvent()) #paint the buffer to the screen

        def updateDrawing(self):
            '''This updates the contents of the buffer'''
            dc = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
            self.draw(dc);

        def OnSize(self,event):
            '''Create the buffer with the size of the window'''
            self.Width, self.Height = self.GetClientSizeTuple()
            self._Buffer = wx.EmptyBitmap(self.Width, self.Height)
            self.update(None);

        def OnPaint(self,event):
            '''Draw the buffer onto the screen'''
            dc = wx.BufferedPaintDC(self, self._Buffer) #this is a weird object that drawns itself to the screen before it dies

        def OnMouseMove(self,event):
                x = event.GetX()
                y = event.GetY()
                newPoint = self.nearestPoint((x,y))
                if self.selectedPoint is not newPoint:
                        self.selectedPoint = newPoint
                        self.update(None)

        def OnClick(self,event):
                '''Work out which point the user is clicking on and inform the game frame'''
                player = self.game.current_player()
                if player in self.players:
                        x = event.GetX()
                        y = event.GetY()
                        point = self.nearestPoint((x,y))
                        if point is not None:
                                try:
                                        self.game.play_move(point,player)
                                except(InvalidMove):
                                        print "Invalid move"

        def OnLeaveWindow(self,event):
                if self.selectedPoint:
                        self.selectedPoint = None #Don't show a stone if the mouse isn't on the board
                        self.updateDrawing()
                        self.GetEventHandler().ProcessEvent(wx.PaintEvent())

class GraphicalDisplayGame(wx.Frame):
	def __init__(self,game,parent=None,id=wx.ID_ANY,title='Go',localPlayers=()): #TODO: option to play GTP player, create object here and call its main loop
                '''localPlayers is a tuple of colors controlled by the GUI.'''
                wx.Frame.__init__(self,parent,id,title,size=(360,400))
                self.panel = wx.Panel(self, wx.ID_ANY)
		self.game = game
                self.localPlayers = localPlayers
                board = BoardImage(game,self.panel,humanPlayers=localPlayers)

                mainSizer = wx.BoxSizer(wx.VERTICAL)
                mainSizer.Add(board,0,wx.FIXED_MINSIZE)

                buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
                passButton = wx.Button(self.panel, wx.ID_ANY, 'Pass')
                resignButton = wx.Button(self.panel, wx.ID_ANY, 'Resign')
                buttonSizer.Add(passButton, 1, wx.ALL|wx.EXPAND)
                buttonSizer.Add(resignButton, 1, wx.ALL|wx.EXPAND)

                mainSizer.Add(buttonSizer,1,wx.ALL|wx.EXPAND)
                self.panel.SetSizer(mainSizer)

                passButton.Bind(wx.EVT_BUTTON, self.passButtonClick)
                resignButton.Bind(wx.EVT_BUTTON, self.resignButtonClick)

        def passButtonClick(self,event):
                if self.game.current_player() in self.localPlayers:
                        self.game.pass_turn()

        def resignButtonClick(self,event):
                if self.game.current_player() in self.localPlayers:
                        self.game.resign()

class GoApp(wx.App):
        def OnInit(self):
                game = TwoPlayerGame((9,9))
#                frame = GraphicalDisplayGame(game,localPlayers=('black','white')) #start a game where both players are controllable
                gnugo = GTPplayer(game,'black','gnugo --mode gtp')
                frame = GraphicalDisplayGame(game,localPlayers=('white')) #start a game where both players are controllable
                frame.Show(True)
                self.SetTopWindow(frame)
                return True

class TextDisplay:
	def __init__(self):
		self.game = None
                print 'Go Game v0.1'

	def draw(self):
                if self.game:
                        boardsize = self.game.board.size
                        print '   '+''.join(['%2d ' %n for n in range(1,boardsize[0]+1)])
                        for j in range(1,boardsize[1]+1):
                                line = []
                                line.append('%2d ' % j)

                                for i in range(1,boardsize[0]+1):
                                        line.append(self.draw_square((i,j)))
                                print ''.join(line)
				
	def draw_square(self,position):
                if self.game:
                        square = self.game.board.square(position)
                        if square.empty():
                                return ' + '
                        elif square.color() == 'black':
                                return ' @ '
                        else:
                                return ' O '

        def interact(self):
                '''Prompt the player for the next move'''
                while not self.game:
                        try:
                                width = int(raw_input('Enter the board width: '))
                                height = int(raw_input('Enter the board height: '))
                                self.game = TwoPlayerGame((width,height))
                        except(ValueError):
                                print "Cannot parse input."

                done = False
                while not done:
                        #prompt for move or command
                        self.draw()
                        print '%s\'s turn.' % self.game.next_player.name
                        move = raw_input('>')

                        if move == 'resign':
                                self.game.resign()
                                done = True
                        elif move == 'pass':
                                self.game.pass_turn()
                        elif move in ('help','?','h'):
                                print 'Enter your move in the form x,y where x is the horizontal coordinate and y is the vertical coordinate.'
                                print 'Other commands:'
                                print '\'pass\' - pass your turn. If both players pass the game is over.'
                                print '\'resign\' - resign the game. Your opponent will win.'
                                print '\'help\' - display this message'
                        elif move in ('go north','go south','go east','go west'): #this is not a text adventure.
                                print 'You have been eaten by a grue.'
                        else:
                                try:
                                        coordinates = move.split(",")
                                        position = (int(coordinates[0]),int(coordinates[1]))
                                        self.game.play_move(position)
                                except(ValueError):
                                        print "Cannot parse input."
                                except(InvalidMove):
                                        print "Invalid move"
                if self.game.winner is not None:
                        print "Winner = " + self.game.winner.name
                                        
                                
