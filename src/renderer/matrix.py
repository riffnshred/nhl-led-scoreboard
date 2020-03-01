from PIL import Image, ImageDraw
from rgbmatrix import graphics
import math

class Matrix:
  def __init__(self, matrix):
    self.matrix = matrix
    self.graphics = graphics
    self.brightness = None

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

  def align_position(self, align, position, size):
    align = align.split("-")
    x, y = position

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
    
    return (x, round(y))

  def draw_text(self, position, text, font, fill=None, align="left", multiline=False):
    if (multiline):
      size = self.draw.multiline_textsize(text, font)
    else:
      size = self.draw.textsize(text, font)

    size = (size[0] - 1, size[1] - 1)

    x, y = self.align_position(align, position, size)

    if (multiline):
      self.draw.multiline_text(
        (round(x) + 1, round(y) - 1), 
        text, 
        fill=fill, 
        font=font,
        align=align.split("-")[0]
      )
    else:
      self.draw.text(
        (round(x) + 1, round(y) - 1), 
        text, 
        fill=fill, 
        font=font
      )

  def draw_image(self, position, image, align="left"):
    position = self.align_position(align, position, image.size)

    try:
      self.image.paste(image, position, image)
    except:
      self.image.paste(image, position)

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

  def draw_text_layout(self, layout, text, font, fill=None, align="left", multiline=False):
    self.draw_text(
      layout.position,
      text,
      fill=fill,
      font=font,
      align=layout.align,
      multiline=multiline
    )

  def draw_pixels_layout(self, layout, pixels, size):
    self.draw_pixels(
      layout.position,
      pixels,
      size,
      layout.align
    )

  def render(self):
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