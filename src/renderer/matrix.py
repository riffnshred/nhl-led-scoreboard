from PIL import Image, ImageDraw
from rgbmatrix import graphics
import math
from utils import round_normal

class Matrix:
  def __init__(self, matrix):
    self.matrix = matrix
    self.graphics = graphics
    self.brightness = None

    self.position_cache = {}

    # Create a new data image.
    self.width = matrix.width
    self.height = matrix.height

    self.image = Image.new('RGBA', (self.width, self.height))
    self.draw = ImageDraw.Draw(self.image)

    self.pixels = self.image.load()

    self.use_canvas = False

    if (self.use_canvas):
      self.canvas = matrix.CreateFrameCanvas()

  def set_brightness(self, brightness):
    self.brightness = brightness
    self.matrix.brightness = self.brightness

  def parse_location(self, value, dimension):
    # Check if number is percentage and calculate pixels
    if (isinstance(value, str) and value.endswith('%')):
      return round_normal((float(value[:-1]) / 100.0) * (dimension - 1))

    return value

  def align_position(self, align, position, size):
    align = align.split("-")
    x, y = position

    # Handle percentages by converting to pixels
    x = self.parse_location(x, self.width)
    y = self.parse_location(y, self.height)

    if (align[0] == "center"):
      x -= size[0] / 2
    elif (align[0] == "right"):
      x -= size[0]

    if (len(align) > 1):
      if (align[1] == "center"):
        y -= size[1] / 2
      elif (align[1] == "bottom"):
        y -= size[1]

    if x % 2 == 0:
      x = math.ceil(x)
    else:
      x = math.floor(x)

    return (round_normal(x), round_normal(y))

  def draw_text(self, position, text, font, fill=None, align="left", multiline=False):
    if (multiline):
      size = self.draw.multiline_textsize(text, font)
    else:
      size = self.draw.textsize(text, font)

    size = (size[0] - 1, size[1] - 1)

    x, y = self.align_position(align, position, size)
    position = (x, y)

    if (multiline):
      self.draw.multiline_text(
        position,
        text, 
        fill=fill,
        font=font,
        spacing=0,
        align=align.split("-")[0]
      )
    else:
      self.draw.text(
        position,
        text, 
        fill=fill, 
        font=font
      )
    
    return {
      "position": position,
      "size": size
    }

  def draw_image(self, position, image, align="left"):
    position = self.align_position(align, position, image.size)

    try:
      self.image.paste(image, position, image)
    except:
      self.image.paste(image, position)

    return {
      "position": position,
      "size": image.size
    }

  def draw_pixel(self, position, color):
    try:
      self.pixels[position] = color
    except:
      print(position, "out of range!")

  def draw_pixels(self, position, pixels, size, align="left"):
    x, y = self.align_position(align, position, size)

    for pixel in pixels:
      self.draw_pixel(
        (
          pixel.position[0] + x,
          pixel.position[1] + y,
        ),
        pixel.color
      )

  def draw_text_layout(self, layout, text, font, align="left", multiline=False):
    self.cache_position(
      layout.id,
      self.draw_text(
        self.layout_position(layout),
        text,
        fill=layout.color,
        font=font,
        align=layout.align,
        multiline=multiline
      )
    )

  def draw_image_layout(self, layout, image, offset=(0, 0)):
    self.cache_position(
      layout.id,
      self.draw_image(
        self.layout_position(layout, offset),
        image,
        layout.align
      )
    )

  def draw_pixels_layout(self, layout, pixels, size):
    self.cache_position(
      layout.id,
      self.draw_pixels(
        self.layout_position(layout),
        pixels,
        size,
        layout.align
      )
    )

  def layout_position(self, layout, offset=(0, 0)):
    x = layout.position[0] + offset[0]
    y = layout.position[1] + offset[1]

    if (hasattr(layout, 'relative') and layout.relative.to in self.position_cache):
      cached_position = self.position_cache[layout.relative.to]
      position = self.align_position(
        layout.relative.align,
        cached_position["position"],
        (
          -cached_position["size"][0],
          -cached_position["size"][1]
        )          
      )

      x += position[0]
      y += position[1]

    return (x, y)

  def cache_position(self, id, position):
    self.position_cache[id] = position

  def render(self):
    for x in range(self.height):
      self.draw_pixel(
        (30, x),
        (0, 255, 0)
      )
      self.draw_pixel(
        (31, x),
        (0, 255, 0)
      )

    if (self.use_canvas):
      self.canvas.SetImage(self.image.convert('RGB'), 0, 0)
      self.canvas = self.matrix.SwapOnVSync(self.canvas)
    else:
      self.matrix.SetImage(self.image.convert('RGB'))

  def clear(self):
    self.image.paste(0, (0, 0, self.width, self.height))

  def network_issue_indicator(self):
    red = self.graphics.Color(255, 0, 0)
    self.graphics.DrawLine(self.matrix, 0, self.matrix.height-1, self.matrix.width, self.matrix.height-1, red)

class MatrixPixels:
  def __init__(self, position, color):
    self.position = position
    self.color = color