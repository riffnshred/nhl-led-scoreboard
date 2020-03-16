from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
import datetime

class Covid_19:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix

        self.all_latest = self.data.covid19_all
        self.layout = self.data.config.config.layout.get_board_layout('covid_19')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

        for case in self.all_latest:
            self.draw_count(self.all_latest[case])
            self.sleepEvent.wait(5)

    def draw_count(self, count):
        self.matrix.clear()
        self.matrix.draw_text_layout(
            self.layout.count,
            str(count)
        )
        
        # self.matrix.draw_text_layout(
        #     self.layout.date, 
        #     self.date.strftime("%b %d %Y")
        # )

        # self.matrix.draw_text_layout(
        #     self.layout.meridiem,
        #     "{}\n{}".format(self.meridiem[0], self.meridiem[1])
        # )

        self.matrix.render()
        if self.data.network_issues and not self.data.config.clock_hide_indicators:
            self.matrix.network_issue_indicator()