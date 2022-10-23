from PIL import Image
import cairosvg
from io import BytesIO
class ImageHelper:


  
  def image_from_svg(url):
    out = BytesIO()
    cairosvg.svg2png(url=url, write_to=out)
    
    img = Image.open(out)
    img = img.crop(img.getbbox())

    return img
