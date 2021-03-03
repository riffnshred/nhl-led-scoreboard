import math
import csv

def get_csv(csvfile):
    #Load csv to get data into a list
    #Make sure file exists
    csv_path = "src/api/weather/" + csvfile
    return list(csv.DictReader(open(csv_path)))


#Take a degree (float) and convert to text and icon   
def degrees_to_direction(degrees):
        try:
            degrees = float(degrees)
        except ValueError:
            return [None,"\uf07b"]

        if degrees < 0 or degrees > 360:
            return [None,"\uf07b"]

        if degrees <= 11.25 or degrees >= 348.76:
            return ["N","\uf060"]
        elif degrees <= 33.75:
            return ["NNE","\uf05e"]
        elif degrees <= 56.25:
            return ["NE","\uf05e"]
        elif degrees <= 78.75:
            return ["ENE","\uf05e"]
        elif degrees <= 101.25:
            return ["E","\uf061"]
        elif degrees <= 123.75:
            return ["ESE","\uf05b"]
        elif degrees <= 146.25:
            return ["SE","\uf05b"]
        elif degrees <= 168.75:
            return ["SSE","\uf05b"]
        elif degrees <= 191.25:
            return ["S","\uf05c"]
        elif degrees <= 213.75:
            return ["SSW","\uf05a"]
        elif degrees <= 236.25:
            return ["SW","\uf05a"]
        elif degrees <= 258.75:
            return ["WSW","\uf05a"]
        elif degrees <= 281.25:
            return ["W","\uf059"]
        elif degrees <= 303.75:
            return ["WNW","\uf05d"]
        elif degrees <= 326.25:
            return ["NW","\uf05d"]
        elif degrees <= 348.75:
            return ["NNW","\uf05d"]
        else:
            return [None,"\uf07b"]

def scale(value, factor):
    """Multiply value by factor, allowing for None values."""
    if value is None:
        return None
    return value * factor

def illuminance_wm2(lux):
    "Approximate conversion of illuminance in lux to solar radiation in W/m2"
    return scale(lux, 0.005)

def pressure_inhg(hPa):
    "Convert pressure from hectopascals/millibar to inches of mercury"
    return scale(hPa, 1 / 33.86389)

def rain_inch(mm):
    "Convert rainfall from millimetres to inches"
    return scale(mm, 1 / 25.4)

def temp_f(c):
    "Convert temperature from Celsius to Fahrenheit"
    if c is None:
        return None
    return (c * 9.0 / 5.0) + 32.0

def wind_kmph(ms):
    "Convert wind from metres per second to kilometres per hour"
    return scale(ms, 3.6)

def wind_mph(ms):
    "Convert wind from metres per second to miles per hour"
    return scale(ms, 3.6 / 1.609344)

def wind_kn(ms):
    "Convert wind from metres per second to knots"
    return scale(ms, 3.6 / 1.852)

_bft_threshold = (
    0.3, 1.5, 3.4, 5.4, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6)

def wind_bft(ms):
    "Convert wind from metres per second to Beaufort scale"
    if ms is None:
        return None
    for bft in range(len(_bft_threshold)):
        if ms < _bft_threshold[bft]:
            return bft
    return len(_bft_threshold)

def dew_point(temp, hum):
    """Compute dew point, using formula from
    http://en.wikipedia.org/wiki/Dew_point.

    """
    if temp is None or hum is None:
        return None
    a = 17.27
    b = 237.7
    gamma = ((a * temp) / (b + temp)) + math.log(float(hum) / 100.0)
    return (b * gamma) / (a - gamma)

def cadhumidex(temp, humidity):
    "Calculate Humidity Index as per Canadian Weather Standards"
    if temp is None or humidity is None:
        return None
    # Formulas are adapted to not use e^(...) with no appreciable
    # change in accuracy (0.0227%)
    saturation_pressure = (6.112 * (10.0**(7.5 * temp / (237.7 + temp))) *
                           float(humidity) / 100.0)
    return temp + (0.555 * (saturation_pressure - 10.0))

def usaheatindex(temp, humidity, dew=None):
    """Calculate Heat Index as per USA National Weather Service Standards

    See http://en.wikipedia.org/wiki/Heat_index, formula 1. The
    formula is not valid for T < 26.7C, Dew Point < 12C, or RH < 40%

    """
    if temp is None or humidity is None:
        return None
    if dew is None:
        dew = dew_point(temp, humidity)
    if temp < 26.7 or humidity < 40 or dew < 12.0:
        return temp
    T = (temp * 1.8) + 32.0
    R = humidity
    c_1 = -42.379
    c_2 = 2.04901523
    c_3 = 10.14333127
    c_4 = -0.22475541
    c_5 = -0.00683783
    c_6 = -0.05481717
    c_7 = 0.00122874
    c_8 = 0.00085282
    c_9 = -0.00000199
    return ((c_1 + (c_2 * T) + (c_3 * R) + (c_4 * T * R) + (c_5 * (T**2)) +
             (c_6 * (R**2)) + (c_7 * (T**2) * R) + (c_8 * T * (R**2)) +
             (c_9 * (T**2) * (R**2))) - 32.0) / 1.8

def wind_chill(temp, wind,units):
    """Compute wind chill, using formula from
    http://en.wikipedia.org/wiki/wind_chill

    """
    if temp is None or wind is None:
        return None

    if units=="kph":
        wind_kph = wind
    else:
        wind_kph = wind * 3.6

    if wind_kph <= 4.8 or temp > 10.0:
        return temp
    return min(13.12 + (temp * 0.6215) +
               (((0.3965 * temp) - 11.37) * (wind_kph ** 0.16)),
               temp)

def apparent_temp(temp, rh, wind,units):
    """Compute apparent temperature (real feel), using formula from
    http://www.bom.gov.au/info/thermal_stress/

    wind must be in m/s
    """
    if units == "kph":
        wind = wind / 3.6

    if temp is None or rh is None or wind is None:
        return None
    vap_press = (float(rh) / 100.0) * 6.105 * math.exp(
        17.27 * temp / (237.7 + temp))
    return temp + (0.33 * vap_press) - (0.70 * wind) - 4.0

def cloud_base(temp, hum):
    """Calculate cumulus cloud base in metres, using formula from
    https://en.wikipedia.org/wiki/Cloud_base or
    https://de.wikipedia.org/wiki/Kondensationsniveau#Konvektionskondensationsniveau
    """
    if temp is None or hum is None:
        return None
    dew_pt = dew_point(temp, hum)
    spread = float(temp) - dew_pt
    return spread * 125.0

def cloud_ft(m):
    "Convert cloud base from metres to feet."
    return scale(m, 3.28084)

