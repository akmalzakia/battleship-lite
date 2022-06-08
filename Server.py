from __future__ import print_function
import random

import sys
from time import sleep, localtime
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from Player import Player

class ServerChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.NextId())
        self.intid = int(self.id)
    
    def PassOn(self, data):
        # pass on what we received to all connected clients
        data.update({"id": self.intid - 1})
        self._server.SendToAll(data)
    
    def Close(self):
        self._server.DelPlayer(self)
    
    ##################################
    ### Network specific callbacks ###
    ##################################
    
    def Network_updatePlayer(self, data):
        self._server.playerList = data['players']
        self.PassOn(data)

    def Network_shouldUpdate(self, data):
        self._server.SendToAll({"action": "shouldUpdate"})
    
    def Network_readySignal(self, data):
        game =  self._server.games[data['gameId']]
        game['players'][self.intid - 1]['isReady'] = True
        isReady = True
        playerIds = []
        for p in game['players']:
          playerIds.append(p['id'])
          if p['isReady'] == False:
            isReady = False
          print(p)

        self.PassOn({"action": "readySignal", "isReady": isReady, "goFirst": random.choice(playerIds)})
    
    def Network_gameOver(self, data):
        self.PassOn(data)


class GameServer(Server):
    channelClass = ServerChannel
    
    def __init__(self, *args, **kwargs):
        self.id = 0
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        self.playerList = []
        self.games = []
        print('Server launched')
    
    def NextId(self):
        self.id += 1
        return self.id
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
        if len(self.playerList) % 2 == 0:
          self.CreateGame()
    
    def CreateGame(self):
        gameId = (self.id - 1) // 2
        playerIds = (self.id - 1, self.id - 2)
        newGame = {'id': gameId, 'isReady': True, 'players': [{'id': playerIds[0], 'isReady': False}, {'id': playerIds[1], 'isReady': False}]}
        self.games.append(newGame)
        self.SendToAll({"action": "startGame", "game": (newGame['id'], newGame['isReady'], playerIds)})
    
    def AddPlayer(self, player):
        print("New Player" + str(player.addr))
        self.players[player] = True
        newPlayer = Player(self.id - 1)
        self.playerList.append(newPlayer)
        player.Send({"action": "initial", "id": self.id - 1})
        self.SendPlayers()
    
    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.SendPlayers()
    
    def SendPlayers(self):
        self.SendToAll({"action": "players", "players": self.playerList})
    
    def SendToAll(self, data):
        [p.Send(data) for p in self.players]
    
    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)

# get command line argument of server, port
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        s = GameServer(localaddr=(host, int(port)))
        s.Launch()