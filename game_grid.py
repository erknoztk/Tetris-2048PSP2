import lib.stddraw as stddraw  # used for displaying the game grid
from lib.color import Color  # used for coloring the game grid
from point import Point  # used for tile positions
import numpy as np  # fundamental Python module for scientific computing
import os
import sys

HIGH_SCORE_FILE = "highscore.txt"

# A class for modeling the game grid
class GameGrid:
   # A constructor for creating the game grid based on the given arguments
   def __init__(self, grid_h, grid_w):
      # set the dimensions of the game grid as the given arguments
      self.grid_height = grid_h
      self.grid_width = grid_w
      # create a tile matrix to store the tiles locked on the game grid
      self.tile_matrix = np.full((grid_h, grid_w), None)
      # create the tetromino that is currently being moved on the game grid
      self.current_tetromino = None
      # the game_over flag shows whether the game is over or not
      self.game_over = False
      # set the color used for the empty grid cells
      self.empty_cell_color = Color(205, 193, 180)
      # set the colors used for the grid lines and the grid boundaries
      self.line_color = Color(187, 173, 160)
      self.boundary_color = Color(187, 173, 160)

      # thickness values used for the grid lines and the grid boundaries
      self.line_thickness = 0.002
      self.box_thickness = 10 * self.line_thickness
      self.score= 0 # initialize score with 0
      self.paused = False # initialize with false for pause button
      self.restart = False  # initilize with false for restart button
      self.score = 0
      self.restart = False
      self.game_over = False
      # load high score
      self.high_score = self.load_high_score()

   # A method for displaying the game grid
   def display(self, next_tetromino=None):
       stddraw.clear(self.empty_cell_color)
       self.draw_grid()
       if self.current_tetromino is not None:
           self.current_tetromino.draw()
       self.draw_boundaries()
       # draw next tetromino in preview page
       if next_tetromino is not None:
           self.draw_next_tetromino(next_tetromino)
        # draw score in preview
       self.draw_score()
       stddraw.show(2)

   # A method for drawing the cells and the lines of the game grid
   def draw_grid(self):
      # for each cell of the game grid
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            # if the current grid cell is occupied by a tile
            if self.tile_matrix[row][col] is not None:
               # draw this tile
               self.tile_matrix[row][col].draw(Point(col, row))
      # draw the inner lines of the game grid
      stddraw.setPenColor(self.line_color)
      stddraw.setPenRadius(self.line_thickness)
      # x and y ranges for the game grid
      start_x, end_x = -0.5, self.grid_width - 0.5
      start_y, end_y = -0.5, self.grid_height - 0.5
      for x in np.arange(start_x + 1, end_x, 1):  # vertical inner lines
         stddraw.line(x, start_y, x, end_y)
      for y in np.arange(start_y + 1, end_y, 1):  # horizontal inner lines
         stddraw.line(start_x, y, end_x, y)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   def draw(self):
      for row in range(self.grid_height):
         for col in range(self.grid_width):
            tile = self.tile_matrix[row][col]
            if tile is not None:
               position = Point(col, row)
               tile.draw(position)

   # A method for drawing the boundaries around the game grid
   def draw_boundaries(self):
      # draw a bounding box around the game grid as a rectangle
      stddraw.setPenColor(self.boundary_color)  # using boundary_color
      # set the pen radius as box_thickness (half of this thickness is visible
      # for the bounding box as its lines lie on the boundaries of the canvas)
      stddraw.setPenRadius(self.box_thickness)
      # the coordinates of the bottom left corner of the game grid
      pos_x, pos_y = -0.5, -0.5
      stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)
      stddraw.setPenRadius()  # reset the pen radius to its default value

   # A method used checking whether the grid cell with the given row and column
   # indexes is occupied by a tile or not (i.e., empty)
   def is_occupied(self, row, col):
      # considering the newly entered tetrominoes to the game grid that may
      # have tiles with position.y >= grid_height
      if not self.is_inside(row, col):
         return False  # the cell is not occupied as it is outside the grid
      # the cell is occupied by a tile if it is not None
      return self.tile_matrix[row][col] is not None

   # A method for checking whether the cell with the given row and col indexes
   # is inside the game grid or not
   def is_inside(self, row, col):
      if row < 0 or row >= self.grid_height:
         return False
      if col < 0 or col >= self.grid_width:
         return False
      return True

   # A method that locks the tiles of a landed tetromino on the grid checking
   # if the game is over due to having any tile above the topmost grid row.
   # (This method returns True when the game is over and False otherwise.)
   def update_grid(self, tiles_to_lock, blc_position):
      # necessary for the display method to stop displaying the tetromino
      self.current_tetromino = None
      # lock the tiles of the current tetromino (tiles_to_lock) on the grid
      n_rows, n_cols = len(tiles_to_lock), len(tiles_to_lock[0])
      for col in range(n_cols):
         for row in range(n_rows):
            # place each tile (occupied cell) onto the game grid
            if tiles_to_lock[row][col] is not None:
               # compute the position of the tile on the game grid
               pos = Point()
               pos.x = blc_position.x + col
               pos.y = blc_position.y + (n_rows - 1) - row
               if self.is_inside(pos.y, pos.x):
                  self.place_tile_without_merge(tiles_to_lock[row][col], pos.x, pos.y)
               # the game is over if any placed tile is above the game grid
               else:
                  self.game_over = True
      for x in range(self.grid_width):
         self.chain_merge_column(x) # do 2048 mentality for each column
      # return the value of the game_over flag
      # clear if line have limit
      self.clear_full_lines()
      return self.game_over

   # chain merge
   def place_tile_without_merge(self, tile, x, y): # put tile to grid
      self.tile_matrix[y][x] = tile
      if tile.position is not None: # tile has position
         tile.position.y = y # update y axis

   def chain_merge_column(self, x):
    # 1. Tüm taşları yukarıdan aşağı topla
    new_column = []
    for y in range(self.grid_height):
        tile = self.tile_matrix[y][x]
        if tile is not None:
            new_column.append(tile)
            self.tile_matrix[y][x] = None

    # 2. Merge işlemini zincirleme şekilde yap
    merged = True
    while merged:
        merged = False
        i = 0
        temp_column = []
        while i < len(new_column):
            if i + 1 < len(new_column) and new_column[i].number == new_column[i + 1].number:
                new_tile = new_column[i]
                new_tile.number *= 2
                self.score += new_tile.number

                new_tile.update_colors()
                temp_column.append(new_tile)
                i += 2
                merged = True
            else:
                temp_column.append(new_column[i])
                i += 1
        new_column = temp_column  # Sonuçla devam et

    # 3. Yeni birleşmiş sütunu yerine koy
    for i, tile in enumerate(new_column):
        self.tile_matrix[i][x] = tile
        if tile.position is not None:
            tile.position.y = i

   def draw_next_tetromino(self, tetromino):
       # determin preview screen X and Y coordinates
       preview_x = self.grid_width + 1
       preview_y = self.grid_height - 4

        # 'Next:' string expression type and color settings
       stddraw.setFontSize(20)
       stddraw.setPenColor(Color(255, 255, 255))
       stddraw.text(preview_x + 1, preview_y + 3, "Next:")

        # take tetromino tile matrix
       tile_matrix = tetromino.tile_matrix
       # draw next tetromino for each block
       for y in range(len(tile_matrix)):
           for x in range(len(tile_matrix[y])):
               tile = tile_matrix[y][x]
               if tile is not None:
                   # calculate positions for each tile
                   draw_x = preview_x + x
                   draw_y = preview_y - y
                   draw_pos = Point(draw_x, draw_y)

                   tile.draw(draw_pos) # draw tile where position which calculated
        # for buttons
       self.draw_buttons()

   def draw_score(self):
       # add score to preview page
       score_x = self.grid_width + 1
       score_y = self.grid_height - 8
        # set up font and color
       stddraw.setFontSize(20)
       stddraw.setPenColor(Color(255, 255, 255))
       stddraw.text(score_x + 1, score_y, f"Score: {self.score}")

   def clear_full_lines(self):
       # when row is full
       new_matrix = [] # matrix hold new row
       total_score = 0 # total score which came from row total
       num_cols = self.grid_width # column nums of row

        # control each row in grid
       for row in self.tile_matrix:
           # if row's col full
           if all(tile is not None for tile in row):
               # do calculation for each tiles
               row_score = sum(tile.number for tile in row if tile is not None)
               total_score += row_score # add current score
               continue  # not add this row to matrix
           new_matrix.append(row)

       #hold row which clear to add new empty row
       num_cleared = self.grid_height - len(new_matrix)

       # adding new row empty
       for _ in range(num_cleared):
           new_matrix.insert(0, [None] * num_cols)
        # add new matris and update grid
       self.tile_matrix = np.array(new_matrix)
       # update current score
       self.score += total_score

   def draw_buttons(self):
       # --PAUSE BUTTON-- #
       stddraw.setPenColor(Color(255, 165, 0))  # orange in RGB
       stddraw.filledRectangle(self.grid_width + 1, self.grid_height - 12, 3, 1.2)
       stddraw.setPenColor(Color(255, 255, 255))  # font color
       stddraw.text(self.grid_width + 2.5, self.grid_height - 11.4, "Pause")

       # --RESTART BUTTON-- #
       stddraw.setPenColor(Color(0, 200, 0))  # green in RGB
       stddraw.filledRectangle(self.grid_width + 1, self.grid_height - 14.5, 3, 1.2)
       stddraw.setPenColor(Color(255, 255, 255)) # font color
       stddraw.text(self.grid_width + 2.5, self.grid_height - 13.9, "Restart")

   def check_button_clicks(self):
       # if no click exit
       if not stddraw.mousePressed():
           return
        # take location of mouse click
       x = stddraw.mouseX()
       y = stddraw.mouseY()

        # set up in preview page buttons
       pause_x = self.grid_width + 1
       pause_y = self.grid_height - 12
       restart_y = self.grid_height - 14.5

        # buttons action
       if pause_x <= x <= pause_x + 3 and pause_y <= y <= pause_y + 1.2:
           self.paused = not self.paused # open/close pause
           while stddraw.mousePressed():
               pass

       elif pause_x <= x <= pause_x + 3 and restart_y <= y <= restart_y + 1.2:
           while stddraw.mousePressed():
               pass
           self.restart = True  #restart flag if click restart func will active

   def reset(self):
       # when click restart, call instructor again and reset game grid
       self.tile_matrix = np.full((self.grid_height, self.grid_width), None)
       self.current_tetromino = None
       self.game_over = False
       self.paused = False
       self.restart = False
       self.score = 0
   def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return int(f.read().strip())
            except:
                return 0
        else:
            return 0

   def save_high_score(self):
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(self.high_score))

    # … diğer metodlar …

   def game_over_screen(self):
        """Game Over ekranını gösterir, tıklamaları bekler."""
        btn_w, btn_h = 4, 1.5
        btn_y = self.grid_height/2 - 4
        x1 = self.grid_width/2 - btn_w - 1  # Restart x
        x2 = self.grid_width/2 + 1           # Exit x

        while True:
            # --- Çizim ---
            stddraw.clear(Color(50, 50, 50))
            stddraw.setFontSize(60)
            stddraw.setPenColor(Color(200, 0, 0))
            stddraw.text(self.grid_width/2, self.grid_height/2 + 4, "GAME OVER")

            stddraw.setFontSize(30)
            stddraw.setPenColor(Color(255, 255, 255))
            stddraw.text(self.grid_width/2, self.grid_height/2 + 1.5, f"Score: {self.score}")
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            stddraw.text(self.grid_width/2, self.grid_height/2 - 0.5,
                         f"High Score: {self.high_score}")

            # Restart butonu
            stddraw.setPenColor(Color(0, 200, 0))
            stddraw.filledRectangle(x1, btn_y, btn_w, btn_h)
            stddraw.setPenColor(Color(255, 255, 255))
            stddraw.setFontSize(20)
            stddraw.text(x1 + btn_w/2, btn_y + btn_h/2, "Restart")

            # Exit butonu
            stddraw.setPenColor(Color(200, 0, 0))
            stddraw.filledRectangle(x2, btn_y, btn_w, btn_h)
            stddraw.setPenColor(Color(255, 255, 255))
            stddraw.text(x2 + btn_w/2, btn_y + btn_h/2, "Exit")

            # Ekranı göster ve olayları işle (100 ms bekle)
            stddraw.show(100)

            # --- Tıklama kontrolü ---
            if stddraw.mousePressed():
                mx, my = stddraw.mouseX(), stddraw.mouseY()
                # Restart alanı
                if x1 <= mx <= x1 + btn_w and btn_y <= my <= btn_y + btn_h:
                    # tıklamayı bırakana kadar bekle
                    while stddraw.mousePressed():
                        pass
                    self.restart = True
                    return
                # Exit alanı
                if x2 <= mx <= x2 + btn_w and btn_y <= my <= btn_y + btn_h:
                    sys.exit()
                # eğer başka yere tıkladıysa, tıklamayı bırakana kadar bekle
                while stddraw.mousePressed():
                    pass





