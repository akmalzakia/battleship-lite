import pygame
import Color

class Grid:
  def __init__(self, offsetX = 0, offsetY = 0) -> None:
    self.grid = []
    self.offsetX = offsetX
    self.offsetY = offsetY
    self.gridSize = (400, 400)
    self.blockSize = 40
    self.width = self.gridSize[0] / self.blockSize
    self.height = self.gridSize[1] / self.blockSize
    self.isLocked = True
  
  def init_grid(self):
    for x in range(0, self.gridSize[0], self.blockSize):
      row = []
      for y in range(0, self.gridSize[1], self.blockSize):
        rect = pygame.Rect(x + self.offsetX, y + self.offsetY, self.blockSize, self.blockSize)
        row.append({'rect': rect, 'isEmpty': True, 'color': Color.RED})
      self.grid.append(row)
  
  def draw_grid(self, screen):
    for x in range(0, int(self.gridSize[0] / self.blockSize) - 1):
      for y in range(0,int(self.gridSize[1] / self.blockSize) - 1):
        pygame.draw.rect(screen, self.grid[x][y]['color'], self.grid[x][y]['rect'], self.grid[x][y]['isEmpty'])
  
  def clicked(self, pos):
    if self.isLocked: return None

    x1 = pos[0]
    y1 = pos[1]
    for x in range(0, int(self.width - 1)):
      for y in range(0, int(self.height - 1)):
        currGrid = self.grid[x][y]['rect']
        if currGrid.x <= x1 <= currGrid.x + currGrid.width and currGrid.y <= y1 <= currGrid.y + currGrid.height:
          return {'pos': (x, y), 'object': self.grid[x][y]}

    return None