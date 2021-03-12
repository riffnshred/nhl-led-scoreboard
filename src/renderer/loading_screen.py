from PIL import Image
from images.image_helper import ImageHelper

PATH = "assets/loading/loading.png"

class Loading:
    def __init__(self, matrix):
        self.matrix = matrix
        self.image = Image.open(PATH)
    def render(self):

        self.matrix.draw_image(
            (0,0),
            self.image
        )
        self.matrix.render()