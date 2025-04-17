# Tetris_2048.py
import time
import lib.stddraw as stddraw  # for animation and user input
from lib.picture import Picture   # for menu image
from lib.color import Color       # for menu colors
import os
import random
from game_grid import GameGrid    # game grid model
from tetromino import Tetromino   # tetromino model

# Simple Point factory for preview positioning
def Point(x, y):
    return type('P', (), {'x': x, 'y': y})()

# Entry point of the game
def start():
    grid_h, grid_w = 15, 12
    # Extend canvas width to fit "Next" preview panel
    canvas_h = 40 * grid_h
    canvas_w = 40 * (grid_w + 4)
    stddraw.setCanvasSize(canvas_w, canvas_h)
    stddraw.setXscale(-0.5, grid_w + 3.5)
    stddraw.setYscale(-0.5, grid_h - 0.5)

    Tetromino.grid_height = grid_h
    Tetromino.grid_width  = grid_w

    grid    = GameGrid(grid_h, grid_w)
    current = create_tetromino()
    next_t  = create_tetromino()
    grid.current_tetromino = current

    display_game_menu(grid_h, grid_w)

    # Draw static preview panel background once
    stddraw.clear(Color(0, 0, 0))
    stddraw.setPenColor(Color(20, 20, 20))
    stddraw.filledRectangle(grid_w - 0.5, -0.5, 4.0, grid_h)
    stddraw.show(0)

    drop_interval = 0.5
    last_drop = time.time()

    while True:
        now = time.time()

        # Process all key events
        while stddraw.hasNextKeyTyped():
            key = stddraw.nextKeyTyped()
            if key == 'left':
                current.move('left', grid)
            elif key == 'right':
                current.move('right', grid)
            elif key == 'down':
                current.move('down', grid)  # soft drop
            elif key == 'up':
                current.rotate(clockwise=True, game_grid=grid)
            elif key == 'space':
                current.drop_bottom(grid)
                shake_effect(grid, current)
            stddraw.clearKeysTyped()

        # Auto-drop mechanism
        if now - last_drop >= drop_interval:
            if not current.move('down', grid):
                tiles, pos = current.get_min_bounded_tile_matrix(True)
                if grid.update_grid(tiles, pos):
                    break  # game over
                current = next_t
                next_t  = create_tetromino()
                grid.current_tetromino = current
                # Redraw static preview background on piece change
                stddraw.setPenColor(Color(20, 20, 20))
                stddraw.filledRectangle(grid_w - 0.5, -0.5, 4.0, grid_h)
            last_drop = now

        # Clear only the grid area each frame
        stddraw.setPenColor(Color(0, 0, 0))
        stddraw.filledRectangle(-0.5, -0.5, grid_w, grid_h)

        # Draw grid and next-preview
        grid.display()
        draw_next_tetromino(next_t)

        stddraw.show(20)

    print('Game over')

# Factory for random tetromino

def create_tetromino():
    return Tetromino(random.choice(['I', 'O', 'Z']))

# Draw the "Next" tetromino preview
def draw_next_tetromino(tetromino):
    stddraw.setFontFamily('Arial')
    stddraw.setFontSize(20)
    stddraw.setPenColor(Color(255, 255, 255))
    stddraw.text(Tetromino.grid_width + 1.5,
                 Tetromino.grid_height - 2,
                 'Next')
    tiles, _ = tetromino.get_min_bounded_tile_matrix(True)
    x_off = Tetromino.grid_width + 1
    y_off = Tetromino.grid_height - 5
    for r, row in enumerate(tiles):
        for c, tile in enumerate(row):
            if tile:
                tile.draw(Point(x_off + c, y_off - r))

# Simple start menu
def display_game_menu(grid_h, grid_w):
    stddraw.clear(Color(42, 69, 99))
    img = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images/menu_image.png')
    stddraw.picture(Picture(img), (grid_w - 1) / 2, grid_h - 7)
    bw, bh = grid_w - 1.5, 2
    bx, by = (grid_w - 1) / 2 - bw / 2, 4
    stddraw.setPenColor(Color(25, 255, 228))
    stddraw.filledRectangle(bx, by, bw, bh)
    stddraw.setFontFamily('Arial')
    stddraw.setFontSize(25)
    stddraw.setPenColor(Color(31, 160, 239))
    stddraw.text((grid_w - 1) / 2, 5, 'Click Here to Start the Game')
    while True:
        stddraw.show(50)
        if stddraw.mousePressed():
            mx, my = stddraw.mouseX(), stddraw.mouseY()
            if bx <= mx <= bx + bw and by <= my <= by + bh:
                return

# Screen shake effect for hard drop
def shake_effect(grid, tetromino):
    for _ in range(5):
        stddraw.setXscale(-0.5 + 0.1, Tetromino.grid_width - 0.5 + 0.1)
        stddraw.clear()
        grid.draw()
        tetromino.draw()
        stddraw.show(20)
        stddraw.setXscale(-0.5 - 0.1, Tetromino.grid_width - 0.5 - 0.1)
        stddraw.clear()
        grid.draw()
        tetromino.draw()
        stddraw.show(20)
    stddraw.setXscale(-0.5, Tetromino.grid_width - 0.5)

if __name__ == '__main__':
    start()


# game_grid.py
import lib.stddraw as stddraw
from lib.color import Color

# Simple Point factory for drawing locked tiles
def Point(x, y):
    return type('P', (), {'x': x, 'y': y})()

class GameGrid:
    def __init__(self, height, width):
        self.height = height
        self.width  = width
        self.grid   = [[None for _ in range(width)] for _ in range(height)]
        self.current_tetromino = None

    def display(self):
        # Draw grid lines
        stddraw.setPenColor(Color(50, 50, 50))
        for r in range(self.height):
            for c in range(self.width):
                stddraw.rectangle(c, r, 1, 1)
        # Draw locked tiles
        for r in range(self.height):
            for c in range(self.width):
                tile = self.grid[r][c]
                if tile:
                    tile.draw(Point(c, r))
        # Draw active tetromino
        if self.current_tetromino:
            self.current_tetromino.draw()

    def update_grid(self, tiles, pos):
        row0, col0 = pos
        for r, row in enumerate(tiles):
            for c, tile in enumerate(row):
                if tile is not None:
                    self.grid[row0 + r][col0 + c] = tile
        # Merge vertical cells of same value
        self.merge_vertical()
        return False  # Game-over logic can be added here

    def merge_vertical(self):
        for col in range(self.width):
            row = 0
            while row < self.height - 1:
                cell  = self.grid[row][col]
                below = self.grid[row + 1][col]
                if cell and below and cell.value == below.value:
                    # Merge into the lower cell
                    below.value *= 2
                    self.grid[row][col] = None
                    # Shift above cells down
                    for r in range(row - 1, -1, -1):
                        self.grid[r + 1][col] = self.grid[r][col]
                    self.grid[0][col] = None
                else:
                    row += 1
