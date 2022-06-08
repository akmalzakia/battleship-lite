
from numpy import block
import pygame

from Grid import Grid


SCREENSIZE = (1000, 1000)
GRIDSIZE = (400, 400)
BLOCKSIZE = 10
class Player:
  def __init__(self, id) -> None:
    self.id = 0
    self.ships = []
    self.shot = []
    self.score = 0
    self.isPlaying = False
    self.isReady = False
  

  
  