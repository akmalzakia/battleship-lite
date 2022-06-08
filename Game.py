from sys import exit
from os import environ
import Color
import pygame

from Grid import Grid

SCREENSIZE = (1000, 1000)
GRIDSIZE = (400, 400)
BLOCKSIZE = 10

environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)

pygame.font.init()
font = pygame.font.SysFont("Arial", 20)
txtpos = (100, 90)

class Game:
    def __init__(self):
        self.ownGrid = Grid(50, 300)
        self.enemyGrid = Grid(550, 300)
        self.statusLabel = "connecting"
        self.playersLabel = "0 players"
        self.frame = 0
        self.isReady = False
        self.isPreparation = True
        self.maxShips = 10
        self.isOver = False

        self.initialize_game()
        
    def initialize_game(self):
        self.ownGrid.init_grid()
        self.enemyGrid.init_grid()

    def Events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == 27):
                exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.isOver:
                  pos = pygame.mouse.get_pos()
                  a_clicked = self.enemyGrid.clicked(pos)
                  if a_clicked and not self.enemyGrid.isLocked:
                    self.attack(a_clicked)

                  d_clicked = self.ownGrid.clicked(pos)
                  if d_clicked and not self.ownGrid.isLocked and self.isPreparation:
                    self.setShip(d_clicked)
                else:
                  exit()
                    
    
    def Draw(self):
        screen.fill([255, 255, 255])
        if not self.isOver:
          if self.isReady:
            if self.isPreparation:
              self.Prepare()
            else:
              self.Start()
          else:
            self.Menu()
        else:
          self.GameOver()

        self.frame += 1
        pygame.display.update()
    
    def Menu(self):
        waiting_text = font.render("Waiting For Player...", 1, Color.RED)
        screen.blit(waiting_text, (SCREENSIZE[0] / 2 - waiting_text.get_width() / 2, SCREENSIZE[1] / 2 - waiting_text.get_height() / 2))

    def Start(self):
        self.manage_turn()
        self.ownGrid.draw_grid(screen)
        self.enemyGrid.draw_grid(screen)
        player = self.players[self.playerId]
        # print(player.isPlaying)

        current_turn_text_t = "Your turn" if player.isPlaying else "Enemy's turn"
        current_turn_text = font.render(current_turn_text_t, 1, Color.BLACK)
        screen.blit(current_turn_text, (SCREENSIZE[0] / 2 - current_turn_text.get_width() / 2, 100))

        your_grid_text = font.render("Your Grid", 1, Color.RED)
        screen.blit(your_grid_text, (self.ownGrid.offsetX + int(self.ownGrid.gridSize[0] / 2) - your_grid_text.get_width(), self.ownGrid.offsetY - 50))
        enemy_grid_text = font.render("Enemy Grid", 1, Color.RED)
        screen.blit(enemy_grid_text, (self.enemyGrid.offsetX + int(self.enemyGrid.gridSize[0] / 2) - your_grid_text.get_width(), self.enemyGrid.offsetY - 50))

        score_text_t = "Your Score : " + str(player.score)
        score_text = font.render(score_text_t, 1, Color.BLACK)
        screen.blit(score_text, (SCREENSIZE[0] / 2 - current_turn_text.get_width() / 2, SCREENSIZE[1] - 100))

    def Prepare(self):
        self.ownGrid.draw_grid(screen)
        prepare_text = font.render("Prepare 10 ships in your own grid by clicking on your grid!", 1, Color.BLACK)
        screen.blit(prepare_text, (SCREENSIZE[0] / 2 - prepare_text.get_width() / 2, 100))
        available_ship_text_t = str(self.maxShips - len(self.players[self.playerId].ships)) + " Available ship left"
        available_ship_text = font.render(available_ship_text_t, 1, Color.BLACK)
        screen.blit(available_ship_text, (self.ownGrid.offsetX + int(self.ownGrid.gridSize[0] / 2) - available_ship_text.get_width() / 2, self.ownGrid.offsetY + self.ownGrid.gridSize[1] + 50))

    def GameOver(self):
        player = self.players[self.playerId]
        if player.score >= self.maxShips:
          self.display_win()
        else:
          self.display_lose()
    
    def display_win(self):
      win_font = pygame.font.SysFont("Arial", 30, True)
      win_text = win_font.render("You Win!", 1, Color.BLACK)
      screen.blit(win_text, (SCREENSIZE[0] / 2 - win_text.get_width() / 2, SCREENSIZE[1] / 2 - win_text.get_height() / 2))
    
    def display_lose(self):
      lose_font = pygame.font.SysFont("Arial", 30, True)
      lose_text = lose_font.render("You Lose!", 1, Color.RED)
      screen.blit(lose_text, (SCREENSIZE[0] / 2 - lose_text.get_width() / 2, SCREENSIZE[1] / 2 - lose_text.get_height() / 2))

   
    def ready_check(self):
        player = self.players[self.playerId]
        if len(player.ships) >= 10:
          player.isReady = True
          self.ownGrid.isLocked = True
          self.sendReadySignal()
        
        self.updatePlayer()
        
       
    
    def attack(self, clicked):
      pos = clicked['pos']
      obj = clicked['object']

      player = self.players[self.playerId]
      enemy = self.players[self.enemyId]
      
      if pos in player.shot:
        return

      # Fill the rectangle
      obj['isEmpty'] = False
      
      player.shot.append(pos)

      # If shot lands on enemy ship
      enemy_ship = next(filter(lambda ship: ship['pos'] == pos, enemy.ships), None)
      if enemy_ship:
        player.score += 1
        obj['color'] = Color.GREEN
        enemy_ship['isSinking'] = True

        if player.score >= self.maxShips:
          self.sendGameOver()

      else:
        obj['color'] = Color.RED
        self.change_turn()

      self.updatePlayer()
      self.sendShouldUpdate()

      


    def setShip(self, clicked):
      pos = clicked['pos']
      obj = clicked['object']

      player = self.players[self.playerId]

      isExist = next(filter(lambda ship: ship['pos'] == pos, player.ships), None)

      if isExist:
        return

      player.ships.append({'pos': pos, 'isSinking': False})

      obj['isEmpty'] = False
      obj['color'] = Color.BLUE

      self.ready_check()


    def update_own_grid(self):
      player = self.players[self.playerId]
      enemy = self.players[self.enemyId]
      sink_list = [ship for ship in player.ships if ship['isSinking'] == True]
      for p in enemy.shot:
        self.ownGrid.grid[p[0]][p[1]]['color'] = Color.RED
        self.ownGrid.grid[p[0]][p[1]]['isEmpty'] = False
 

      for p in sink_list:
        pos = p['pos']
        self.ownGrid.grid[pos[0]][pos[1]]['color'] = Color.BLACK
        self.ownGrid.grid[pos[0]][pos[1]]['isEmpty'] = False
      
    def manage_turn(self):
      if self.players[self.playerId].isPlaying:
        self.enemyGrid.isLocked = False
      else:
        self.enemyGrid.isLocked = True
  
    def change_turn(self):
      player = self.players[self.playerId]
      enemy = self.players[self.enemyId]
      player.isPlaying = False
      enemy.isPlaying = True