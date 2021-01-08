# NHL Data refresh module.

def daily(data):
    print('refreshing data')
    # Update team's data
    data.get_teams_info()

    # Get the teams info
    data.teams = data.get_teams()

    # Get favorite team's id
    data.pref_teams = data.get_pref_teams_id()

    # Update standings
    data.refresh_standings()

    # Fetch the playoff data
    data.refresh_playoff()

