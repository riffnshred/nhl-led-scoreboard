from PIL import Image, ImageDraw
from rgbmatrix import graphics
import math
from utils import round_normal
import sys
import numpy as np

DEBUG = False


# A fake class to fill in the __init__ of Matrix
class TermMatrix:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def SetImage(self, img):
        show_image(img)

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
                y -= size[1] / 2 + 1
            elif (align[1] == "bottom"):
                y -= size[1]

        if x % 2 == 0:
            x = math.ceil(x)
        else:
            x = math.floor(x)

        return (round_normal(x), round_normal(y))

    def draw_text(self, position, text, font, fill=None, align="left",
                backgroundColor=None, backgroundOffset=[1, 1, 1, 1]):
        width = 0
        height = 0
        text_chars = text.split("\n")
        offsets = []

        for index, chars in enumerate(text_chars):
            spacing = 0 if index == 0 else 1

            # deprecated in pillow==9.5.0
            #offset = font.getoffset(chars)
            #offset_x = offset[0]
            #offset_y = offset[1] - height - spacing

            # for pillow>=10.0.0
            left, top, right, bottom = font.getbbox(chars)
            offset_x = left
            offset_y = top - height - spacing

            offsets.append((offset_x, offset_y))

            bounding_box = font.getmask(chars).getbbox()
            if bounding_box is not None:
                width = bounding_box[2] if bounding_box[2] > width else width
                height += bounding_box[3] + spacing

        width -= 1
        height -= 1
        size = (width, height)

        x, y = self.align_position(align, position, size)

        if (backgroundColor != None):
            self.draw_rectangle(
            (x - backgroundOffset[0], y - backgroundOffset[1]),
            (width + backgroundOffset[0] + backgroundOffset[2], height + backgroundOffset[1] + backgroundOffset[3]),
            backgroundColor
        )

        if (backgroundColor != None):
            self.draw_rectangle(
            (x - backgroundOffset[0], y - backgroundOffset[1]),
            (width + backgroundOffset[0] + backgroundOffset[2], height + backgroundOffset[1] + backgroundOffset[3]),
            backgroundColor
        )
        
        
        for index, chars in enumerate(text_chars):
            offset = offsets[index]
            chars_position = (x - offset[0], y - offset[1])
            self.draw.text(
                chars_position,
                chars,
                fill=fill,
                font=font
            )

        if (DEBUG):
            self.draw_pixel(
                (x, y),
                (0, 255, 0)
            )
            self.draw_pixel(
                (x, y + height),
                (0, 255, 0)
            )
            self.draw_pixel(
                (x + width, y + height),
                (0, 255, 0)
            )
            self.draw_pixel(
                (x + width, y),
                (0, 255, 0)
            )

        return {
            "position": (x, y),
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

    def draw_rectangle(self, position, size, color):
        self.draw.rectangle(
            [
            position[0],
            position[1],
            position[0] + size[0],
            position[1] + size[1]
            ],
            fill=color
        )

        return {
            "position": position,
            "size": size
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

    def draw_text_layout(self, layout, text, align="left", fillColor=None, backgroundColor=None):
        if fillColor == None:
            fillColor = layout.color
        self.cache_position(
            layout.id,
            self.draw_text(
                self.layout_position(layout),
                text,
                fill=fillColor,
                font=layout.font,
                backgroundColor=backgroundColor, #layout.backgroundColor if hasattr(layout, 'backgroundColor') else None,
                align=layout.align
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
        if (DEBUG):
            for x in range(self.height):
                self.draw_pixel(
                    (self.width / 2 - 1, x),
                    (0, 255, 0)
                )
                self.draw_pixel(
                    (self.width / 2, x),
                    (0, 255, 0)
                )

            for x in range(self.width):
                self.draw_pixel(
                    (x, self.height / 2 - 1),
                    (0, 255, 0)
                )
                self.draw_pixel(
                    (x, self.height / 2),
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
        self.graphics.DrawLine(self.matrix, 0, self.matrix.height - 1, self.matrix.width, self.matrix.height - 1, red)

    def update_indicator(self):
        green = self.graphics.Color(0, 255, 0)
        self.graphics.DrawLine(self.matrix, 0, 0, self.matrix.width,0, green)


class MatrixPixels:
    def __init__(self, position, color):
        self.position = position
        self.color = color


def get_ansi_color_code(r, g, b):
    if r == g and g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)


def get_color(r, g, b):
    return "\x1b[48;5;{}m \x1b[0m".format(int(get_ansi_color_code(r,g,b)))


def show_image(img):
    h = img.height
    w = img.width

    # Get image
    img = img.resize((w,h), Image.ANTIALIAS)
    # Set to array
    img_arr = np.asarray(img)
    # Get the shape so we know x,y coords
    h,w,c = img_arr.shape

    # Then draw our mona lisa
    mona_lisa = ''
    for x in range(h):
        for y in range(w):
            pix = img_arr[x][y]
            color = ' '
            # 90% of our image is black, and the pi sometimes has trouble writing to the terminal
            # quickly. So default the color to blank, and only fill in the color if it's not black
            if sum(pix) > 0:
                color = get_color(pix[0], pix[1], pix[2])
            mona_lisa += color
    sys.stdout.write(mona_lisa)
    sys.stdout.flush()
