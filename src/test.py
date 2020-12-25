import cairosvg
from io import BytesIO
from urllib.request import Request, urlopen

print("running")

urllib.request.urlretrieve("https://cdn.nhle.com/logos/nhl/svg/BOS_light.svg", "local-filename.svg")

print("Done !")