from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from datetime import datetime, timedelta
from utils import convert_time
import random

class Covid_19:
    def __init__(self, data, matrix, sleepEvent):
        self.data = data
        self.matrix = matrix
        self.data.covid19.get_all()
        self.layout = self.data.config.config.layout.get_board_layout('covid_19')
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.time_format = self.data.config.time_format

        if data.config.covid_ww_board_enabled or (not data.config.covid_ww_board_enabled and not data.config.covid_country_board_enabled and not data.config.covid_us_state_board_enabled and not data.config.covid_canada_board_enabled):
            try:
                self.worldwide_data = self.data.covid19.ww
                self.last_update = convert_time((datetime(1970, 1, 1) + timedelta(milliseconds=self.worldwide_data['updated'])).strftime("%Y-%m-%dT%H:%M:%SZ")).strftime(self.get_time_format(self.time_format))
                self.data.network_issues = False
                for case in self.worldwide_data:
                    if case not in ("cases", "deaths", "recovered"):
                        continue
                    self.draw_count(case, self.worldwide_data[case],  self.last_update, "WW")
                    self.sleepEvent.wait(5)
            except ValueError as e:
                print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                self.data.network_issues = True

        self.last_update = datetime.now().strftime(self.get_time_format(self.time_format))

        if data.config.covid_country_board_enabled:
            self.country = data.config.covid_country
            count = 0
            for i in self.country:
                try:
                    self.data.network_issues = False
                    self.country_data = self.data.covid19.countrydict[self.country[count]]
                    for case in self.country_data:
                        if case not in ("cases", "todayCases", "deaths","todayDeaths", "recovered","critical"):
                            continue
                        if case == "todayDeaths":
                            self.draw_count("Todays Deaths", self.country_data[case],  self.last_update, self.country[count][0:3])
                            self.sleepEvent.wait(3)
                        elif case == "todayCases":
                            self.draw_count("Today's Cases", self.country_data[case],  self.last_update, self.country[count][0:3])
                            self.sleepEvent.wait(3)
                        else:
                            self.draw_count(case, self.country_data[case],  self.last_update, self.country[count][0:3])
                            self.sleepEvent.wait(3)
                except ValueError as e:
                    print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                    self.data.network_issues = True
                count += 1

        if data.config.covid_us_state_board_enabled:
            self.us_state = data.config.covid_us_state
            count = 0
            for i in self.us_state:
                try:
                    self.data.network_issues = False
                    self.us_state_data = self.data.covid19.us_state_dict[self.us_state[count]]
                    for case in self.us_state_data:
                        if case not in ("cases", "todayCases", "deaths","todayDeaths"):
                            continue
                        if case == "todayDeaths":
                            self.draw_count("Todays Deaths", self.us_state_data[case],  self.last_update, self.us_state[count])
                            self.sleepEvent.wait(3)
                        elif case == "todayCases":
                            self.draw_count("Today's Cases", self.us_state_data[case],  self.last_update, self.us_state[count])
                            self.sleepEvent.wait(3)
                        else:
                            self.draw_count(case, self.us_state_data[case],  self.last_update, self.us_state[count])
                            self.sleepEvent.wait(3)  
                except ValueError as e:
                    print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                    self.data.network_issues = True
                count += 1
        
        if data.config.covid_canada_board_enabled:
            self.canada_prov = data.config.covid_canada_prov
            count = 0
            for i in self.canada_prov: 
                try:
                    self.data.network_issues = False
                    self.canada_prov_data = self.data.covid19.canada_prov_dict[self.canada_prov[count]]
                    self.canada_location = self.canada_prov_data['province']
                    for case in self.canada_prov_data['stats']:
                        if case not in ("confirmed", "deaths", "recovered"):
                            continue
                        else:
                            self.draw_count(case, self.canada_prov_data['stats'][case],  self.last_update, self.canada_location)
                            self.sleepEvent.wait(3)  
                except ValueError as e:
                    print("NETWORK ERROR, COULD NOT GET NEW COVID 19 DATA: {}".format(e))
                    self.data.network_issues = True
                count += 1        


    def get_time_format(self,time_flag):
        if time_flag == "%H:%M":
            time_flag = "%m/%d %H:%M:%S"
        else:
            time_flag = "%m/%d %I:%M:%S %P"
        return time_flag

    def draw_count(self, name, count, last_update, location):

        banner = {
            "cases":{
                "color":(255, 165, 0),
                "width": 20
            },
            "deaths":{
                "color":(255, 10, 10),
                "width": 24
            },
            "recovered":{
                "color":(0, 255, 0),
                "width": 36
            },
            "Today's Cases":{
                "color":(255, 165, 0),
                "width":48
            },
            "Todays Deaths":{
                "color":(255, 10, 10),
                "width":50
            },
            "critical":{
                "color":(255, 165, 0),
                "width": 28
            },
            "confirmed":{
                "color":(255, 165, 0),
                "width": 34
            }
        }
        us_state_abbrev = {
            'Alabama': 'AL',
            'Alaska': 'AK',
            'American Samoa': 'AS',
            'Arizona': 'AZ',
            'Arkansas': 'AR',
            'California': 'CA',
            'Colorado': 'CO',
            'Connecticut': 'CT',
            'Delaware': 'DE',
            'District Of Columbia': 'DC',
            'Florida': 'FL',
            'Georgia': 'GA',
            'Guam': 'GU',
            'Hawaii': 'HI',
            'Idaho': 'ID',
            'Illinois': 'IL',
            'Indiana': 'IN',
            'Iowa': 'IA',
            'Kansas': 'KS',
            'Kentucky': 'KY',
            'Louisiana': 'LA',
            'Maine': 'ME',
            'Maryland': 'MD',
            'Massachusetts': 'MA',
            'Michigan': 'MI',
            'Minnesota': 'MN',
            'Mississippi': 'MS',
            'Missouri': 'MO',
            'Montana': 'MT',
            'Nebraska': 'NE',
            'Nevada': 'NV',
            'New Hampshire': 'NH',
            'New Jersey': 'NJ',
            'New Mexico': 'NM',
            'New York': 'NY',
            'North Carolina': 'NC',
            'North Dakota': 'ND',
            'Northern Mariana Islands':'MP',
            'Ohio': 'OH',
            'Oklahoma': 'OK',
            'Oregon': 'OR',
            'Pennsylvania': 'PA',
            'Puerto Rico': 'PR',
            'Rhode Island': 'RI',
            'South Carolina': 'SC',
            'South Dakota': 'SD',
            'Tennessee': 'TN',
            'Texas': 'TX',
            'Utah': 'UT',
            'Vermont': 'VT',
            'United States Virgin Islands': 'VI',
            'Virginia': 'VA',
            'Washington': 'WA',
            'West Virginia': 'WV',
            'Wisconsin': 'WI',
            'Wyoming': 'WY'
        }
        prov_terr = {
            'Alberta': 'AB',
            'British Columbia':'BC',
            'Manitoba': 'MB',
            'New Brunswick': 'NB',
            'Newfoundland and Labrador': 'NL',
            'Northwest Territories': 'NT',
            'Nova Scotia': 'NS',
            'Nunavut': 'NU',
            'Ontario': 'ON',
            'Prince Edward Island': 'PE',
            'Quebec': 'QC',
            'Saskatchewan': 'SK',
            'Yukon': 'YT'
        }
        try:
            location = us_state_abbrev[location] 
        except:
            location = location
        try:
            location = prov_terr[location]
        except:
            location = location

        self.matrix.clear()

        self.matrix.draw_text_layout(
            self.layout.board_title,
            "COVID-19".upper(),
            backgroundColor=(0, 255, 0)
        )

        self.matrix.draw_text_layout(
            self.layout.lastupdate,
            f"{last_update} ".upper()
        )
        self.matrix.draw_text_layout(
            self.layout.count,
            str(count)
        )      
        
        self.matrix.draw_text_layout(
            self.layout.location,
            location.upper()
        )
        
        self.matrix.draw_text_layout(
            self.layout.name,
            name.upper(),
            backgroundColor=banner[name]["color"]
        )
        
        for i in range(30):
            self.matrix.draw_pixel((random.randrange(30, 35), random.randrange(0, 7)), (0,random.randrange(90, 255),0))

        for i in range(10):
            self.matrix.draw_pixel((random.randrange(35, 40), random.randrange(3, 7)), (0,random.randrange(30, 200),0))
        
        for i in range(5):
            self.matrix.draw_pixel((random.randrange(40, 45), random.randrange(5, 7)), (0,random.randrange(30, 160),0))
            
        self.matrix.render()

        if self.data.network_issues:
            self.matrix.network_issue_indicator()
        
        if self.data.newUpdate and not self.data.config.clock_hide_indicators:
            self.matrix.update_indicator()