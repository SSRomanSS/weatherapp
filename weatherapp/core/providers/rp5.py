# -*- coding: utf-8 -*-
"""
rp5 provider
"""
import sys
from urllib.parse import quote
import re
from htmldom import htmldom

from weatherapp.core import config
from weatherapp.core.abstract import WeatherProvider


class Rp5WeatherProvider(WeatherProvider):
    """
    RP5.ua
    """
    title = config.RP5_TITLE
    provider_name = config.RP5_SHORTCUT
    city = config.CITY
    url = config.RP5_URL

    def create_default_settings(self):
        """

        :return:
        """
        city = self.city
        url = self.url
        provider_name = self.provider_name
        self.save_settings(city, url, provider_name)

    def create_settings(self, provider_name):
        """

        :param provider_name:
        :return:
        """

        city = ''
        url = ''
        link_set, locations_list, location_name, location_link = \
            config.RP5_SET, config.RP5_LIST, config.RP5_NAME, config.RP5_LINK
        content = self.get_page_content(link_set)
        dom = htmldom.HtmlDom(link_set)
        dom = dom.createDom()

        while content:
            search_list = []
            if len(locations_list) == 1:
                search_content = content.find_all(locations_list[0][0], locations_list[0][1])
                if not search_content:
                    search_content = content.find_all(config.RP5_VAR[0], config.RP5_VAR[1])
                    # for some ending pages from RP5 that have a different tag structure
            else:
                search_content = content.find_all(locations_list[0][0], locations_list[0][1])
                locations_list = locations_list[1:]

            ind = 0
            for i in search_content:
                print(i.find(location_name[0][0], location_name[0][1]).text, '-', ind)
                search_list.append((i.find(location_name[0][0], location_name[0][1]).text,
                                    i.find(location_link[0][0], location_link[0][1])['href']))
                ind += 1
            if search_list:
                try:
                    select = int(input('Make your choice, input the number:\n>'))
                except ValueError:
                    msg = 'You input not number. Restart'
                    if self.app.commands.debug:
                        self.app.logger.exception(msg)
                    else:
                        self.app.logger.error(msg)
                    sys.exit()
                try:
                    content = self.get_page_content(
                        dom.baseURL + '/' +
                        quote(search_list[select][1], encoding='utf8'))
                except IndexError:
                    msg = 'Selected number is not in list'
                    if self.app.commands.debug:
                        self.app.logger.exception(msg)
                    else:
                        self.app.logger.error(msg)
                    sys.exit()
                url = dom.baseURL + '/' + quote(search_list[select][1])
                city = search_list[select][0]
            else:
                break
        self.save_settings(city, url, provider_name)

    @staticmethod
    def get_weather_info(page_content):
        """ Collect weather information
        """

        current_day = page_content.find('div', id='ftab_1_content')

        weather_info = {'Conditions': '-', 'Temperature': '-', 'Feels like': '-', 'Wind': '-'}
        if current_day:
            weather_info['Conditions'] = re.search(r'b>.*</b',
                                                   current_day.find('div',
                                                                    class_='cc_0')
                                                   .div['onmouseover']).group()[2:-3]
            temp = current_day.find('div', class_='t_0')
            if temp:
                weather_info['Temperature'] = temp.text
                wind = current_day.find('td', class_='wn')
                if wind:
                    weather_info['Wind'] = re.search(r', .*,',
                                                     current_day.find('td',
                                                                      class_='wn')
                                                     .div['onmouseover']).group()[3:-3]

        return weather_info
