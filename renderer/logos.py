from PIL import Image

class TeamLogos:
    def __init__(self, matrix, layout, team, gameLocation):
        self.matrix = matrix
        self.layout = layout
        self.team = team
        self.gameLocation = gameLocation

    def render(self):
        # Get the on-screen position of both logos
        logo_pos = self.layout.get_scoreboard_logo_coord(self.team.id)[self.gameLocation]

        # Open the logo image file
        team_logo = Image.open('logos/{}.png'.format(self.team.abbrev))

        # Put the images on the canvas
        self.matrix.draw_image((logo_pos["x"], logo_pos["y"]), team_logo)

