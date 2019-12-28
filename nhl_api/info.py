import nhl_api.data
import nhl_api.object

def team_info():
    """
    Returns a list of team information dictionaries

    """
    data = nhl_api.data.get_teams()
    parsed = data.json()
    teams_data = parsed["teams"]
    teams = []

    for team in teams_data:
        team_id = team['id']
        name = team['name']
        abbreviation = team['abbreviation']
        team_name = team['teamName']
        location_name = team['locationName']
        short_name = team['shortName']
        division_id = team['division']['id']
        division_name = team['division']['name']
        division_abrev = team['division']['abbreviation']
        conference_id = team['conference']['id']
        conference_name = team['conference']['name']
        official_site_url = team['officialSiteUrl']
        franchise_id = team['franchiseId']

        output = {
            'team_id': team_id,
            'name': name,
            'abbreviation': abbreviation,
            'team_name': team_name,
            'location_name': location_name,
            'short_name': short_name,
            'division_id': division_id,
            'division_name': division_name,
            'division_abrev': division_abrev,
            'conference_id': conference_id,
            'conference_name': conference_name,
            'official_site_url': official_site_url,
            'franchise_id': franchise_id
        }

        # put this dictionary into the larger dictionary
        teams.append(output)

    return teams

def status():
    data = nhl_api.data.get_game_status().json()
    return data

def current_season():
    data = nhl_api.data.get_current_season().json()
    return data

class Info(nhl_api.object.Object):
    pass