import random

import lib.stddraw as stddraw  # used for drawing the tiles to display them
from lib.color import Color  # used for coloring the tiles

# A class for modeling numbered tiles as in 2048
class Tile:
   # Class variables shared among all Tile objects
   # ---------------------------------------------------------------------------
   # the value of the boundary thickness (for the boxes around the tiles)
   boundary_thickness = 0.004
   # font family and font size used for displaying the tile number
   font_family, font_size = "Arial", 14

   # A constructor that creates a tile with special color and value
   def __init__(self):
      # set the number on this tile
      self.number = random.choice([2,4])

      #determine color for which number which color
      bg_rgb, fg_rgb = Tile.get_tile_colors(self.number)
      self.background_color = Color(*bg_rgb)
      self.foreground_color = Color(*fg_rgb)

      self.box_color = Color(187, 173, 160)

   # A method for drawing this tile at a given position with a given length
   def draw(self, position, length=1):  # length defaults to 1
      # draw the tile as a filled square
      stddraw.setPenColor(self.background_color)
      stddraw.filledSquare(position.x, position.y, length / 2)
      # draw the bounding box around the tile as a square
      stddraw.setPenColor(self.box_color)
      stddraw.setPenRadius(Tile.boundary_thickness)
      stddraw.square(position.x, position.y, length / 2)
      stddraw.setPenRadius()  # reset the pen radius to its default value
      # draw the number on the tile
      stddraw.setPenColor(self.foreground_color)
      stddraw.setFontFamily(Tile.font_family)
      stddraw.setFontSize(Tile.font_size)
      stddraw.text(position.x, position.y, str(self.number))

   #each number has own color
   @staticmethod
   def get_tile_colors(number):
      color_map = {
         2: ((238, 228, 218), (119, 110, 101)),
         4: ((237, 224, 200), (119, 110, 101)),
         8: ((242, 177, 121), (255, 255, 255)),
         16: ((245, 149, 99), (255, 255, 255)),
         32: ((246, 124, 95), (255, 255, 255)),
         64: ((246, 94, 59), (255, 255, 255)),
         128: ((237, 207, 114), (255, 255, 255)),
         256: ((237, 204, 97), (255, 255, 255)),
         512: ((237, 200, 80), (255, 255, 255)),
         1024: ((237, 197, 63), (255, 255, 255)),
         2048: ((237, 194, 46), (255, 255, 255)),
      }

      return color_map.get(number, ((60, 58, 50), (255, 255, 255)))

   def update_colors(self):
      bg_rgb, fg_rgb = Tile.get_tile_colors(self.number)
      self.background_color = Color(*bg_rgb)
      self.foreground_color = Color(*fg_rgb)

