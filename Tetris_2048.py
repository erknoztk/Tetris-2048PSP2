import lib.stddraw as stddraw
from lib.picture import Picture
from lib.color import Color
import os
import random
from game_grid import GameGrid
from tetromino import Tetromino

def start():
   grid_h, grid_w = 15, 12


   canvas_h, canvas_w = 40 * grid_h, 40 * (grid_w + 5)
   stddraw.setCanvasSize(canvas_w, canvas_h)
   stddraw.setXscale(-0.5, grid_w + 4.5)
   stddraw.setYscale(-0.5, grid_h - 0.5)

   Tetromino.grid_height = grid_h
   Tetromino.grid_width = grid_w

   grid = GameGrid(grid_h, grid_w)
   display_game_menu(grid_h, grid_w)

   while True:  #
      current_tetromino = create_tetromino()
      next_tetromino = create_tetromino()
      grid.current_tetromino = current_tetromino

      while not grid.game_over:
         grid.check_button_clicks()

         if grid.restart:
            grid.reset()
            current_tetromino = create_tetromino()
            next_tetromino = create_tetromino()
            grid.current_tetromino = current_tetromino
            continue  # game reset after restart

         if grid.paused:
            grid.display(next_tetromino)
            continue

         if stddraw.hasNextKeyTyped():
            key_typed = stddraw.nextKeyTyped()
            if key_typed == "left":
               current_tetromino.move("left", grid)
            elif key_typed == "right":
               current_tetromino.move("right", grid)
            elif key_typed == "down":
               current_tetromino.move("down", grid)
            elif key_typed == "up":
               current_tetromino.rotate(clockwise=True, game_grid=grid)
            elif key_typed == "space":
               current_tetromino.drop_bottom(grid)
               shake_effect(grid, current_tetromino, next_tetromino)

            stddraw.clearKeysTyped()

         success = current_tetromino.move("down", grid)
         if not success:
            tiles, pos = current_tetromino.get_min_bounded_tile_matrix(True)
            game_over = grid.update_grid(tiles, pos)
            if game_over:
               break
            current_tetromino = next_tetromino
            next_tetromino = create_tetromino()
            grid.current_tetromino = current_tetromino

         grid.display(next_tetromino)

      if not grid.restart:
         break

   print("Game over")


def create_tetromino():
   tetromino_types = ['I', 'O', 'Z', 'S', 'T', 'J', 'L']
   random_type = random.choice(tetromino_types)
   return Tetromino(random_type)

def display_game_menu(grid_height, grid_width):
   background_color = Color(42, 69, 99)
   button_color = Color(25, 255, 228)
   text_color = Color(31, 160, 239)

   stddraw.clear(background_color)
   current_dir = os.path.dirname(os.path.realpath(__file__))
   img_file = current_dir + "/images/menu_image.png"
   img_center_x, img_center_y = (grid_width - 1) / 2, grid_height - 7
   image_to_display = Picture(img_file)
   stddraw.picture(image_to_display, img_center_x, img_center_y)

   button_w, button_h = grid_width - 1.5, 2
   button_blc_x, button_blc_y = img_center_x - button_w / 2, 4

   stddraw.setPenColor(button_color)
   stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)

   stddraw.setFontFamily("Arial")
   stddraw.setFontSize(25)
   stddraw.setPenColor(text_color)
   stddraw.text(img_center_x, 5, "Click Here to Start the Game")

   while True:
      stddraw.show(50)
      if stddraw.mousePressed():
         mouse_x, mouse_y = stddraw.mouseX(), stddraw.mouseY()
         if button_blc_x <= mouse_x <= button_blc_x + button_w and \
            button_blc_y <= mouse_y <= button_blc_y + button_h:
            break

def shake_effect(grid, current_tetromino, next_tetromino):
   for i in range(5):
      stddraw.setXscale(-0.5 + 0.1, grid.grid_width + 4.5 + 0.1)  # preview panel dahil
      stddraw.clear()
      grid.draw()
      current_tetromino.draw()
      grid.draw_next_tetromino(next_tetromino)
      stddraw.show(20)

      stddraw.setXscale(-0.5 - 0.1, grid.grid_width + 4.5 - 0.1)
      stddraw.clear()
      grid.draw()
      current_tetromino.draw()
      grid.draw_next_tetromino(next_tetromino)
      stddraw.show(20)

   stddraw.setXscale(-0.5, grid.grid_width + 4.5)



if __name__ == '__main__':
   start()
