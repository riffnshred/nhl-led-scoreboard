# Weather Observations and Alerts Boards

## DISCLAIMER
Whenever lives or financial decisions may be impacted by weather events, professional advice and forecasts should be sought from qualified meteorologists.  The weather information is provided by 3rd parties and we are not responsible for the accuracy or content of information contained in those sites provided.

## Python Requirements
The weather and alert boards require certain python libraries in order to function properly.   These python packages can be installed using pip3:
env-canada>=0.0.35
noaa-sdk>=0.1.18
pyowm>=3.0.0


## Description

There are 2 boards that have been created to provide current weather observations and weather alerts. For the observations, there are two data feeds used: Environment Canada (EC) (no api key required) and Open Weather Map (OWM) (API key required). OWM can be used worldwide for observations while EC is for Canada only. For weather alerts, there are also two feeds: EC (Canada only) and National Weather Service (NWS) (US Only). The Weather observation board (called weather) can be added to any of the states (off\_day, scheduled, intermission or post\_game) while the Alerts board will &quot;interrupt&quot; any currently displayed board once and then the alert will be added as an extra page in the main weather board. Both the weather and alert boards use your latitude and longitude based on the IP address of your Raspberry Pi to get the weather information.

## Board Name

The name of the board that can be added to the different states is : **weather**

### Weather Configuration in config.json

| Setting | Type | Parameters | Description |
| --- | --- | --- | --- |
| enabled | Bool | true,false | Use the weather board |
| units | String | metric,imperial | Units to use for weather display |
| duration | INT | 30 | The time to flip through the pages in the weather board. If there are no alerts, this will be 3 pages, if there are alerts a 4th is added. Minimum 30 seconds duration|
| data\_feed | String | EC,OWM | Where is the observation data coming from. You can use EC for Environment Canada, OWM for Open Weather Map (requires API KEY from https://openweathermap.org/api) |
| alert\_feed | String | EC,NWS | What data feed is provide alert data. EC for Environment Canada or NWS for the National Weather Service in the US |
| owm\_apikey | String | |API key required for when you use OpenWeatherMAP. https://openweathermap.org/api |
| update\_freq | INT | 5 | How often in minutes to refresh the weather feed. Less than 5 minutes will not provide any value. |
| show\_alerts | Bool | true,false | Get weather alerts and display them |
| alert\_title | Bool | true,false | On the initial alert page that will interrupt the normal board rotation, display on the top and bottom board the type of alert (WARNING, WATCH or ADVISORY) |
| scroll\_alert | Bool | true,false | Scroll the text of the alert on the initial alert page. If you select false, a static page will be displayed that is the same as the 4th page on the weather board |
| alert\_duration | INT | 5 | How long to show alert board (in seconds). This is for the non-scrolling alert board. |
| show\_on\_clock | Bool | true,false | Add the last observed temperature and humidity to the bottom of the clock board |
| view | String | full, summary | Weather board full (3 page) or summary view (1 page) |

> ***NOTE*** When you register for an OWM API key, it can take up to a day before it is activated. Select the Current Weather Data one as that's what the pyowm library uses.  Also, you are limited on the number of API calls you can make, so choose your update time accordingly.  5 minutes makes the most sense as the lowest amonunt of time you can do API calls.

### How the weather board looks

The weather board will consist of 3 pages normally with a 4th page when there are alerts.

#### First Page

![1stpage](../../../assets/images/wx1stpage.jpg)

The green temperature is actual temperature while the red is the &quot;feels like&quot; temperature. The icon on the right is the graphical representation of the current condition which is shown in text below the &quot;feels like&quot; temperature. The bottom line is the last updated time

#### Second Page

![2ndpage](../../../assets/images/wx2ndpage.jpg)

This page consists of the wind direction and speed, wind gusts and visibility. The icon shows the direction that the wind is blowing from.

#### Third Page

![3rdpage](../../../assets/images/wx3rdpage.jpg)

This page consists of the pressure, dew point (the temperature where water can condense) and humidity. For EC feed, the arrow in the top right will show the pressure tendency (rising, falling or level). For OWM, this will show NA.

#### Fourth Page

![4thpage](../../../assets/images/wx4thpage.png)

The 4th page will consist of the type of alert (warning, watch or advisory) on the bottom of the screen, the type of alert in the middle (in white lettering and smaller as well as the time the alert was issued) and the word weather on the top. The top 1/3 and bottom 1/3 of the screen will also have colored bars that reflect the type of alert based on if it&#39;s a warning, watch or advisory. The colors are the same as the local weather provider uses. For EC, a warning is red, watch yellow and advisory is grey. For NWS, warning is red, watch is orange and advisory is yellow.

#### Clock w/ temperature and humidity

![wxClock](../../../assets/images/wxClock.jpg)


### The Alert Board

The alert board can be static (which will be identical to the 4th page on the weather board) or have scrolling. The scrolling version will be similar to the image below.  The board will only display the latest and highest level alert issued.  This is a design choice due to the massive amounts of alerts that the NWS will issue that overlap.  It is too cumbersome to have a screen displayed for each one.

![AlertScroll](../../../assets/images/wxAlertscroll.jpg)

