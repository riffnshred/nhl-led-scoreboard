from PIL import Image, ImageDraw
from rgbmatrix import graphics

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

  def draw_text(self, position, text, font, fill=None,
          align="left", multiline=False):
    x, y = position

    if (multiline):
      size = self.draw.multiline_textsize(text, font)
    else:
      size = self.draw.textsize(text, font)

    align = align.split("-")

    if (align[0] == "center"):
      x -= size[0] / 2
    elif (align[0] == "right"):
      x -= size[0]

    if (len(align) > 1):
      if (align[1] == "center"):
        y -= size[1] / 2
      elif (align[1] == "bottom"):
        y -= size[1]

    if (multiline):
      self.draw.multiline_text(
        (round(x), round(y) - 1), 
        text, fill=fill, font=font,
        align=align[0]
      )
    else:
      self.draw.text((round(x), round(y) - 1), text, fill=fill, font=font)

  def draw_image(self, position, image, align="left"):
    x, y = position

    align = align.split("-")

    if (align[0] == "center"):
      x -= image.size[0] / 2
    elif (align[0] == "right"):
      x -= image.size[0]

    if (len(align) > 1):
      if (align[1] == "center"):
        y -= size[1] / 2
      elif (align[1] == "bottom"):
        y -= size[1]

    try:
      self.image.paste(image, (round(x), round(y)), image)
    except:
      self.image.paste(image, (round(x), round(y)))

  def set_pixel(self, position, color):
    self.pixels[position] = color

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
