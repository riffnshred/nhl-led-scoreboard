from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime

class Covid_19:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix
        try:
            self.data.covid19.get_all()
            self.data.network_issues = False
        except ValueError as e:
            print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: " + e)
            self.data.network_issues = True

        self.worldwide_data = self.data.covid19.all
        self.layout = self.data.config.config.layout.get_board_layout('covid_19')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        for case in self.worldwide_data:
            self.draw_count(case, self.worldwide_data[case])
            self.sleepEvent.wait(5)

    def draw_count(self, name, count):

        name_layout = {
            "position": [0, -2],
            "align": "left-bottom",

            "relative": {
                "to": "count",
                "align": "left-top"
            }
        }

        case_colors = {
            "cases":[255,0,0]
        }

        self.matrix.clear()
        self.matrix.draw_text_layout(
            self.layout.count,
            str(count)
        )
        
        self.matrix.draw_text(
                name_layout,
                name.upper(),
                font="_default"
            )


        # self.matrix.draw_text_layout(
        #     self.layout.meridiem,
        #     "{}\n{}".format(self.meridiem[0], self.meridiem[1])
        # )

        self.matrix.render()
        if self.data.network_issues:
            self.matrix.network_issue_indicator()