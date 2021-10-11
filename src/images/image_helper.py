from PIL import Image
import cairosvg
""" from svglib.svglib import svg2rlg
from reportlab.lib.utils import ImageReader
from reportlab.graphics import renderPM """
from io import BytesIO

class ImageHelper:
  def image_from_svg(url):
    out = BytesIO()
    cairosvg.svg2png(url=url, write_to=out)
    #out.seek(0)
    #out = ImageReader(url)
    img = Image.open(out)
    img = img.crop(img.getbbox())

    return img
