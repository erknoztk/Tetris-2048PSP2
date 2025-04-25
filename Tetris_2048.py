import lib.stddraw as stddraw
from lib.picture import Picture
from lib.color import Color
import os
import random
from game_grid import GameGrid
from tetromino import Tetromino

def start():
    grid_h, grid_w = 15, 12
    canvas_h, canvas_w = 40*grid_h, 40*(grid_w+5)
    stddraw.setCanvasSize(canvas_w, canvas_h)
    stddraw.setXscale(-0.5, grid_w+4.5)
    stddraw.setYscale(-0.5, grid_h-0.5)

    Tetromino.grid_height = grid_h
    Tetromino.grid_width  = grid_w

    grid = GameGrid(grid_h, grid_w)
    display_game_menu(grid_h, grid_w)

    # Dış döngü: Kullanıcı restart yapana veya exit diyene kadar devam eder
    while True:
        # beginning of each game reset
        grid.reset()
        current = create_tetromino()
        nxt     = create_tetromino()
        grid.current_tetromino = current

        # Maç döngüsü
        while True:
            # Pause/Restart butonları (oyun içi)
            grid.check_button_clicks()
            if grid.restart:
                # Restart tuşuna basıldı: bu maç bitti, dış döngü başa dönsün
                break

            # Eğer paused durumdaysak sadece çiz
            if grid.paused:
                grid.display(nxt)
                continue

            # — Klavye kontrolleri —
            if stddraw.hasNextKeyTyped():
                key = stddraw.nextKeyTyped()
                if key == "left":
                    current.move("left", grid)
                elif key == "right":
                    current.move("right", grid)
                elif key == "down":
                    current.move("down", grid)
                elif key == "up":
                    current.rotate(clockwise=True, game_grid=grid)
                elif key == "space":
                    current.drop_bottom(grid)
                    shake_effect(grid, current, nxt)
                stddraw.clearKeysTyped()
            # ————————

            # autonom move for tetromino and game
            success = current.move("down", grid)
            if not success:
                tiles, pos = current.get_min_bounded_tile_matrix(True)
                if grid.update_grid(tiles, pos):
                    # if gameover true show GAMEOVER screen
                    grid.game_over = True
                    while True:
                        grid.game_over_screen()
                       
                        # click restart
                        if grid.restart:
                            break

                    break  # exit game
                # game not finish
                current = nxt
                nxt     = create_tetromino()
                grid.current_tetromino = current

            # draw tetromino each move
            grid.display(nxt)

        # Buraya geldiğimizde ya Restart basıldı, ya da exit yapıldı
        if not grid.restart:
            # Exit’e basıldı: döngüyü kır, program sonlansın
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
     # shift the X-scale to the right to simulate shake
      stddraw.setXscale(-0.5 + 0.1, grid.grid_width + 4.5 + 0.1)  # include preview
      stddraw.clear() #clear screen
      grid.draw() # draw current state of the grid
      current_tetromino.draw() # draw the tetromino which fall
      grid.draw_next_tetromino(next_tetromino) #draw next tetromino
      stddraw.show(20) # show the frame with slight delay for visibility
    # do for same thing when shift he X-scale to the right
      stddraw.setXscale(-0.5 - 0.1, grid.grid_width + 4.5 - 0.1)
      stddraw.clear()
      grid.draw()
      current_tetromino.draw()
      grid.draw_next_tetromino(next_tetromino)
      stddraw.show(20)

   stddraw.setXscale(-0.5, grid.grid_width + 4.5)



if __name__ == '__main__':
   start()
