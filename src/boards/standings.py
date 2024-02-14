from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from time import sleep
import debug

class Standings:
    """
        TODO: Change draw standings to use new matrix layout system
    """
    def __init__(self, data, matrix,sleepEvent):
        self.conferences = ["eastern", "western"]
        self.divisions = ["metropolitan", "atlantic", "central", "pacific"]
        self.data = data
        self.matrix = matrix
        self.team_colors = data.config.team_colors
        self.sleepEvent= sleepEvent
        self.sleepEvent.clear()

    def render(self):
        if self.data.standings:
            type = self.data.config.standing_type
            if self.data.config.preferred_standings_only:
                if type == 'conference':
                    conference = self.data.config.preferred_conference
                    records = getattr(self.data.standings.by_conference, conference)
                    # calculate the image height
                    im_height = (len(records) + 1) * 7
                    # Increment to move image up
                    i = 0
                    image = draw_standing(self.data, conference, records, im_height, self.matrix.width)
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    #sleep(5)
                    self.sleepEvent.wait(5)
                    # Move the image up until we hit the bottom.
                    while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                        i -= 1
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        #sleep(0.2)
                        self.sleepEvent.wait(0.2)
                    # Show the bottom before we change to the next table.
                    #sleep(5)
                    self.sleepEvent.wait(5)

                elif type == 'division':
                    division = self.data.config.preferred_divisions
                    records = getattr(self.data.standings.by_division, division)
                    # calculate the image height
                    im_height = (len(records) + 1) * 7
                    # Increment to move image up
                    i = 0
                    image = draw_standing(self.data, division, records, im_height, self.matrix.width)
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    #sleep(5)
                    self.sleepEvent.wait(5)

                    # Move the image up until we hit the bottom.
                    while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                        i -= 1
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        #sleep(0.2)
                        self.sleepEvent.wait(0.2)
                    # Show the bottom before we change to the next table.
                    #sleep(5)
                    self.sleepEvent.wait(5)

                elif type == 'wild_card':
                    wildcard_records = {}
                    conf_name = self.data.config.preferred_conference
                    conf_data = getattr(self.data.standings.by_wildcard, conf_name)
                    wildcard_records["conference"] = conf_name
                    division_leaders = {}
                    for record_type, value in vars(conf_data).items():
                        if record_type == "wild_card":
                            wildcard_records["wild_card"] = value
                        else:
                            for div_name, div_record in vars(value).items():
                                division_leaders[div_name] = div_record

                            wildcard_records["division_leaders"] = division_leaders

                    # initialize the number_of_rows at 10 (conference name + 2x Division name + wildcard title + 6x Division leaders record)
                    number_of_rows = 10 + len(wildcard_records["wild_card"])

                    # Space between each table in row of LED
                    table_offset = 3

                    # Total Height in row of LED. each record and table titles need 7 row of LED plus the space between each tables (3 tables means 2 space between each)
                    img_height = (number_of_rows * 7) + (table_offset * 2)

                    # Increment to move image up
                    i = 0
                    image = draw_wild_card(self.data, wildcard_records, self.matrix.width, img_height, table_offset)
                    self.matrix.draw_image((0, i), image)
                    self.matrix.render()
                    #sleep(5)
                    self.sleepEvent.wait(5)
                    # Move the image up until we hit the bottom.
                    while i > -(img_height - self.matrix.height) and not self.sleepEvent.is_set():
                        i -= 1
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        #sleep(0.2)
                        self.sleepEvent.wait(0.2)
                    #sleep(5)
                    self.sleepEvent.wait(5)
            else:
                if type == 'conference':
                    for conference in self.conferences:
                        records = getattr(self.data.standings.by_conference, conference)
                        # calculate the image height
                        im_height = (len(records) + 1) * 7
                        # Increment to move image up
                        i = 0
                        image = draw_standing(self.data, conference, records, im_height, self.matrix.width)
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        if self.data.network_issues:
                            self.matrix.network_issue_indicator()
                        
                        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                            self.matrix.update_indicator()

                        #sleep(5)
                        self.sleepEvent.wait(5)

                        # Move the image up until we hit the bottom.
                        while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                            i -= 1
                            self.matrix.draw_image((0, i), image)
                            self.matrix.render()
                            if self.data.network_issues:
                                self.matrix.network_issue_indicator()

                            if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                                self.matrix.update_indicator()
                                
                            #sleep(0.2)
                            self.sleepEvent.wait(0.2)
                        # Show the bottom before we change to the next table.
                        #sleep(5)
                        self.sleepEvent.wait(5)

                elif type == 'division':
                    for division in self.divisions:
                        records = getattr(self.data.standings.by_division, division)
                        # calculate the image height
                        im_height = (len(records) + 1) * 7
                        # Increment to move image up
                        i = 0
                        image = draw_standing(self.data, division, records, im_height, self.matrix.width)
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        #sleep(5)
                        self.sleepEvent.wait(5)

                        # Move the image up until we hit the bottom.
                        while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                            i -= 1
                            self.matrix.draw_image((0, i), image)
                            self.matrix.render()
                            #sleep(0.2)
                            self.sleepEvent.wait(0.2)
                        # Show the bottom before we change to the next table.
                        #sleep(5)
                        self.sleepEvent.wait(5)
                elif type == 'wild_card':
                    wildcard_records = {}
                    for conf_name, conf_data in vars(self.data.standings.by_wildcard).items():
                        wildcard_records["conference"] = conf_name
                        division_leaders = {}
                        for record_type, value in vars(conf_data).items():
                            if record_type == "wild_card":
                                wildcard_records["wild_card"] = value
                            else:
                                for div_name, div_record in vars(value).items():
                                    division_leaders[div_name] = div_record
                                wildcard_records["division_leaders"] = division_leaders
                        # initialize the number_of_rows at 10 (conference name + 2x Division name + wildcard title + 6x Division leaders record)
                        number_of_rows = 10 + len(wildcard_records["wild_card"])
                        # Space between each table in row of LED
                        table_offset = 3
                        # Total Height in row of LED. each record and table titles need 7 row of LED plus the space between each tables (3 tables means 2 space between each)
                        img_height = (number_of_rows * 7) + (table_offset * 2)
                        # Increment to move image up
                        i = 0
                        image = draw_wild_card(self.data, wildcard_records, self.matrix.width, img_height, table_offset)
                        self.matrix.draw_image((0, i), image)
                        self.matrix.render()
                        #sleep(5)
                        self.sleepEvent.wait(5)
                        # Move the image up until we hit the bottom.
                        while i > -(img_height - self.matrix.height) and not self.sleepEvent.is_set():
                            i -= 1
                            self.matrix.draw_image((0, i), image)
                            self.matrix.render()
                            #sleep(0.2)
                            self.sleepEvent.wait(0.2)
                        #sleep(5)
                        self.sleepEvent.wait(5)
        else:
            debug.error("Standing board unavailable due to missing information from the API")


def draw_standing(data, name, records, img_height, width):
    """
        Draw an image of a list of standing record of each team.
        :return the image
    """

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
        abbrev = team["teamAbbrev"]["default"]
        team_id = data.teams_info_by_abbrev[abbrev].details.id
        points = str(team["points"])
        wins = team["wins"]
        losses = team["losses"]
        ot = team["otLosses"]
        team_colors = data.config.team_colors
        bg_color = team_colors.color("{}.primary".format(team_id))
        txt_color = team_colors.color("{}.text".format(team_id))
        draw.rectangle([0, row_pos, 12,top + row_pos], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, row_pos), abbrev, fill=(txt_color['r'], txt_color['g'], txt_color['b']), font=layout.font)
        if len(points) == 3:
            draw.text((54, row_pos), points, font=layout.font)
        else:
            draw.text((57, row_pos), points, font=layout.font)
        draw.text((19, row_pos), "{}-{}-{}".format(wins, losses, ot), font=layout.font)
        row_pos += row_height

    return image


def draw_wild_card(data, wildcard_records, width, img_height, offset):
    """
        Draw an image of a list of standing record of each team.
        This is the Wild card version which is a bit more elaborate. need to figure a way to merge both draw_standings
        and draw_wild_card together.
        :return image
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

    draw.text((1, 0), wildcard_records["conference"], font=layout.font)
    row_pos += row_height
    for division, division_data in wildcard_records["division_leaders"].items():
        draw.text((1, row_pos), division, font=layout.font)
        row_pos += row_height
        for team in division_data["teamRecords"]:
            abbrev = team.team_abbrev.default
            team_id = data.teams_info_by_abbrev[abbrev].details.id
            points = str(team.points)
            wins = team.wins
            losses = team.losses
            ot = team.ot_losses
            team_colors = data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))
            draw.rectangle([0, row_pos, 12, top + row_pos], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
            draw.text((1, row_pos), abbrev, fill=(txt_color['r'], txt_color['g'], txt_color['b']), font=layout.font)
            if len(points) == 3:
                draw.text((54, row_pos), points, font=layout.font)
            else:
                draw.text((57, row_pos), points, font=layout.font)
            draw.text((19, row_pos), "{}-{}-{}".format(wins, losses, ot), font=layout.font)
            row_pos += row_height
        # add a space of one row of 2 LED between each tables
        row_pos += offset

    draw.text((1, row_pos), "wild card", font=layout.font)
    row_pos += row_height
    for team in wildcard_records["wild_card"]:
        abbrev = team.team_abbrev.default
        team_id = data.teams_info_by_abbrev[abbrev].details.id
        points = str(team.points)
        wins = team.wins
        losses = team.losses
        ot = team.ot_losses
        team_colors = data.config.team_colors
        bg_color = team_colors.color("{}.primary".format(team_id))
        txt_color = team_colors.color("{}.text".format(team_id))
        draw.rectangle([0, top + row_pos, 12, row_pos], fill=(bg_color['r'], bg_color['g'], bg_color['b']))
        draw.text((1, row_pos), abbrev, fill=(txt_color['r'], txt_color['g'], txt_color['b']), font=layout.font)
        if len(points) == 3:
            draw.text((54, row_pos), points, font=layout.font)
        else:
            draw.text((57, row_pos), points, font=layout.font)
        draw.text((19, row_pos), "{}-{}-{}".format(wins, losses, ot), font=layout.font)
        row_pos += row_height

    return image
