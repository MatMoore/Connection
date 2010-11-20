from subprocess import *

class GTPplayer:
	'''Object which sends GTP command to interact with other players'''
	def __init__(self,game,color,command):
			self.process = Popen(command,stdin=PIPE,stdout=PIPE,stderr=PIPE,shell=True)
			print 'send boardsize... '+ self._sendCommand('boardsize %d %d' % game.board.size)
			print 'send komi... '+ self._sendCommand('komi %f' % game.komi)
			self.color = color
			self.game = game
			print 'listen'
			self._listen() #get first move
			game.attach(self) #watch for changes

	def _listen(self):
			'''query the player for the next move, and then attempt to play it'''
			player = self.game.current_player() 
			if player == self.color:
					output=self._sendCommand('genmove '+self.color).rstrip()
					output = self._preprocess(output)
					print 'generated move '+output
					if output[0]=='=':
							output = output.lstrip('= ').lower()
							if output == 'resign': #implement this later
									pass
							elif output == 'pass':
									pass #TODO implement this and make pass function in game accept player argument
							else:
									letter = output[0]
									y = int(output[1:])
									x = ord(letter)-ord('a') + 1
									if letter>'i':
											x -= 1
									self.game.play_move((x,y),player)						

	def _notify(self,move):
		'''Tell the player where the other player played'''
		print 'sending move '+str(move)
		print self._sendCommand('play '+str(move))

	def _sendCommand(self,command):
		self.process.stdin.write(command+'\n')
		output = self.process.stdout.readline()
		self.process.stdout.readline() #take care of extra \n at the end of the repsonse
		return output

	def _preprocess(self,command):
		'''remove all control chars except HT and LF, convert HT to space'''
		return command

	def update(self,object):
		'''Called when the game or board change'''
		print 'got last move'
		lastMove = self.game.last_move()
		if lastMove and lastMove.player.color is not self.color:
			print 'notify'
			self._notify(lastMove)
		self._listen() #problem - if >2 players then cant genmove straight away - start a new thread which waits for turn?
		pass

class GTPreceiver:
		'''Object which responds to GTP commands. '''
		pass
