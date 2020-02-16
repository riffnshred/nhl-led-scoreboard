"""
TODO: add Wildcard.
"""
from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep


class Standings:
    def __init__(self, data, matrix):
        self.conferences = ["eastern", "western"]
        self.divisions = ["metropolitan", "atlantic", "central", "pacific"]
        self.data = data
        self.matrix = matrix
        self.team_colors = data.config.team_colors

    def render(self):
        type = self.data.config.standing_type
        if self.data.config.preferred_standings_only:
            if type == 'conference':
                conference = self.data.config.preferred_conference
                records = getattr(self.data.standings.by_conference, conference)
                # calculate the image height
                im_height = (len(records) + 1) * 7
                # Increment to move image up
                i = 0
                image = draw_records(self.data, conference, records, im_height, self.matrix.width)
                self.matrix.draw_image((0, i), image)
                self.matrix.render()
                sleep(5)
                # Move the image up until we hit the bottom.
                while i > -(im_height - self.matrix.height):
                    i -= 1
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    sleep(0.2)
                # Show the bottom before we change to the next table.
                sleep(5)

            elif type == 'division':
                division = self.data.config.preferred_divisions
                records = getattr(self.data.standings.by_division, division)
                # calculate the image height
                im_height = (len(records) + 1) * 7
                # Increment to move image up
                i = 0
                image = draw_records(self.data, division, records, im_height, self.matrix.width)
                self.matrix.draw_image((0, i), image)
                self.matrix.render()
                sleep(5)

                # Move the image up until we hit the bottom.
                while i > -(im_height - self.matrix.height):
                    i -= 1
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    sleep(0.2)
                # Show the bottom before we change to the next table.
                sleep(5)
        else:
            if type == 'conference':
                for conference in self.conferences:
                    records = getattr(self.data.standings.by_conference, conference)
                    # calculate the image height
                    im_height = (len(records) + 1) * 7
                    # Increment to move image up
                    i = 0
                    image = draw_records(self.data, conference, records, im_height, self.matrix.width)
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    if self.data.network_issues:
                        self.matrix.network_issue_indicator()
                    sleep(5)

                    # Move the image up until we hit the bottom.
                    while i > -(im_height - self.matrix.height):
                        i -= 1
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        if self.data.network_issues:
                            self.matrix.network_issue_indicator()
                        sleep(0.2)
                    # Show the bottom before we change to the next table.
                    sleep(5)

            elif type == 'division':
                for division in self.divisions:
                    records = getattr(self.data.standings.by_division, division)
                    # calculate the image height
                    im_height = (len(records) + 1) * 7
                    # Increment to move image up
                    i = 0
                    image = draw_records(self.data, division, records, im_height, self.matrix.width)
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    sleep(5)

                    # Move the image up until we hit the bottom.
                    while i > -(im_height - self.matrix.height):
                        i -= 1
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        sleep(0.2)
                    # Show the bottom before we change to the next table.
                    sleep(5)


def draw_records(data, name, records, img_height, width):
    """
        Draw an image of a list of standing record of each team.
        :return the image
    """

    teams_info = data.teams_info
    layout = data.config.layout

    # Create a new data image.
    image = Image.new('RGB', (width, img_height))
    draw = ImageDraw.Draw(image)

    """
        Each record info is shown in a row of 7 pixel high. The initial row start at pixel 0 (top screen). For each
        team's record we add an other row and increment the row position by the height of a row plus the 
        incrementation "i".
    """
    row_pos = 0
    row_height = 7
    top = row_height - 1  # For some reason, when drawing with PIL, the first row is not 0 but -1

    draw.text((1, 0), name, font=layout.font)
    row_pos += row_height

    for team in records:
        pos = team['conferenceRank']
        team_id = team['team_id']
        abbev = teams_info[team_id].abbreviation
        points = str(team['points'])
        wins = team['leagueRecord']['wins']
        losses = team['leagueRecord']['losses']
        ot = team['leagueRecord']['ot']
        team_colors = data.config.team_colors
        bg_color = team_colors.color("{}.primary".format(team_id))
        txt_color = team_colors.color("{}.text".format(team_id))
        draw.rectangle([0, top + row_pos, 12, row_pos], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, row_pos), abbev, fill=(txt_color['r'], txt_color['g'], txt_color['b']), font=layout.font)
        draw.text((57, row_pos), points, font=layout.font)
        draw.text((19, row_pos), "{}-{}-{}".format(wins, losses, ot), font=layout.font)
        row_pos += row_height

    return image
