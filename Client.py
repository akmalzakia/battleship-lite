from __future__ import print_function

import sys
from time import sleep

from PodSixNet.Connection import connection, ConnectionListener
from Game import Game

class Client(ConnectionListener, Game):
    def __init__(self, host, port):
        self.Connect((host, port))
        self.players = []
        Game.__init__(self)
    
    def Loop(self):
        self.Pump()
        connection.Pump()
        self.Events()
        self.Draw()
        
    #######################    
    ### Event callbacks ###
    #######################
    #def PenDraw(self, e):
    #    connection.Send({"action": "draw", "point": e.pos})
    
    def updatePlayer(self):
        connection.Send({"action": "updatePlayer", "players": self.players})
    
    def sendShouldUpdate(self):
        connection.Send({"action": "shouldUpdate"})
    
    def sendReadySignal(self):
        connection.Send({"action": "readySignal", "gameId": self.gameId, "id": self.playerId})
    
    def sendGameOver(self):
        connection.Send({"action": "gameOver"})
    
    ###############################
    ### Network event callbacks ###
    ###############################
    
    def Network_initial(self, data):
        self.playerId = data['id']
    
    def Network_startGame(self, data):
        game = data['game']
        self.gameId = game[0]
        self.isReady = game[1]
        self.enemyId = tuple(filter(lambda x: x is not self.playerId, game[2]))[0]
        self.ownGrid.isLocked = False
    
    def Network_updatePlayer(self, data):
        self.players = data['players']
    
    def Network_players(self, data):
        self.playersLabel = str(len(data['players'])) + " players"
        self.players = data['players']

    def Network_shouldUpdate(self, data):
        self.update_own_grid()
    
    def Network_readySignal(self, data):
        if data['isReady']:
          if self.playerId == data['goFirst']:
            self.players[self.playerId].isPlaying = True
            self.updatePlayer()

          self.isPreparation = False
          self.manage_turn()

    def Network_gameOver(self, data):
        self.isOver = True
        
    def Network(self, data):
        #print('network:', data)
        pass
    
    def Network_connected(self, data):
        self.statusLabel = "connected"
    
    def Network_error(self, data):
        print(data)
        import traceback
        traceback.print_exc()
        self.statusLabel = data['error'][1]
        connection.Close()
    
    def Network_disconnected(self, data):
        self.statusLabel += " - disconnected"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        c = Client(host, int(port))
        while 1:
            c.Loop()
            sleep(0.001)