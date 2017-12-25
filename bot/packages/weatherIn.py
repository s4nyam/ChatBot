# -*- coding: utf-8 -*-
import json
import requests
import mapps
from colorama import Fore


def main(self, s):
    loc = s.replace('weather ', '').replace('in ', '')  # Trim input command to get only the location

    # Checks country
    country = mapps.getLocation()['country_name']

    # If country is US, shows weather in Fahrenheit
    if country == 'United States':
        send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=imperial".format(loc)
        )
        unit = ' ºF in '

    # If country is not US, shows weather in Celsius
    else:
        send_url = (
            "http://api.openweathermap.org/data/2.5/weather?q={0}"
            "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units=metric".format(loc)
        )
        unit = ' ºC in '
    r = requests.get(send_url)
    j = json.loads(r.text)
    temperature = j['main']['temp']
    description = j['weather'][0]['main']
    print(Fore.BLUE + "It's " + str(temperature) + unit + str(loc.title()) + " (" + str(description) + ")" + Fore.RESET)