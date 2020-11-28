from PIL import Image
from utils import get_file
import debug

class StanleyCupChampions:
    def __init__(self, data, matrix, sleepEvent):
        
        self.team_id = data.ScChampions_id
        print(data.ScChampions_id)
        self.team_abbrev = data.teams_info[self.team_id].abbreviation
        self.data = data
        self.team_info = data.teams_info[self.team_id]
        self.matrix = matrix
        self.team_colors = data.config.team_colors
        self.font = data.config.layout.font
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

    def render(self):
        print("Display stanleycup champions {} ".format(self.data.teams_info[self.team_id].abbreviation))
        self.matrix.clear()
        bg_img = Image.open(get_file('assets/images/stanleycupchamps_bg.png'))
        self.matrix.draw_image((0,0), bg_img)

        # If there is a Stanley cup champion, show the board. Else, pass
        if self.team_id:
            team_color_main = self.team_colors.color("{}.primary".format(self.team_id))
            team_color_accent = self.team_colors.color("{}.text".format(self.team_id))


            self.matrix.render()
            self.sleepEvent.wait(0.5)
            self.matrix.draw_text(
                (18, 7), 
                self.team_abbrev,
                font=self.font,
                fill=(team_color_accent['r'], team_color_accent['g'], team_color_accent['b']),
                backgroundColor=(team_color_main['r'], team_color_main['g'], team_color_main['b']),
                backgroundOffset=[6, 1, 6, 1]
            )
            self.matrix.render()
            self.sleepEvent.wait(0.5)
            self.matrix.draw_text(
                (37, 7), 
                str(self.data.year), 
                font=self.font, 
                fill=(0, 0, 0),
                backgroundColor=(200,200,200)
            )
            self.matrix.render()
            self.sleepEvent.wait(0.5)
            self.matrix.draw_text(
                (12, 14), 
                "STANLEY CUP", 
                font=self.font, 
                fill=(255,255,255),
            )
            self.matrix.render()
            self.sleepEvent.wait(0.5)
            self.matrix.draw_text(
                (16, 21), 
                "CHAMPIONS",
                font=self.font,
                fill=(team_color_accent['r'], team_color_accent['g'], team_color_accent['b']),
                backgroundColor=(team_color_main['r'], team_color_main['g'], team_color_main['b']),
                backgroundOffset=[4, 1, 4, 1]
            )
            self.matrix.render()
            self.sleepEvent.wait(10)
        else:
            debug.info("No Stanley Cup Champions, going to next board")