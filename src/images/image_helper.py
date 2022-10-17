from PIL import Image
from io import BytesIO
import requests
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


class ImageHelper:


  
  def image_from_svg(url):
    response = requests.get(url)
    bytes = BytesIO(response.content)
    drawing = svg2rlg(bytes)
    renderPM.drawToFile(drawing, "_tmp.png", fmt="PNG")

    return Image.open("_tmp.png")
