from PIL import Image
class TeamLogos:
    def __init__(self, away, home, coords, canvas):
        self.coords = coords
        self.canvas = canvas
        self.away = away
        self.home = home

    def render(self):
        # Get the on-screen position of both logos
        away_team_logo_pos, home_team_logo_pos = self.coords._get_scoreboard_logo_coord(self.away.id, self.home.id)

        # Open the logo image file
        away_team_logo = Image.open('logos/{}.png'.format(self.away.abbrev))
        home_team_logo = Image.open('logos/{}.png'.format(self.home.abbrev))

        # Put the images on the canvas
        self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
        self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

