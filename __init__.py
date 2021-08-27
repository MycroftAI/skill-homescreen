# Copyright 2021 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
import os
import time
import requests
from datetime import datetime, timedelta
from os import path
from pathlib import Path

from mycroft.messagebus.message import Message
from mycroft.skills import MycroftSkill, resting_screen_handler, intent_handler, intent_file_handler
from mycroft.skills.skill_loader import load_skill_module
from mycroft.skills.skill_manager import SkillManager
from mycroft.util.format import nice_time, nice_date
from mycroft.util.time import now_local

FIFTEEN_MINUTES = 900
MARK_II = "mycroft_mark_2"
ONE_MINUTE = 60
TEN_SECONDS = 10


class MycroftHomescreen(MycroftSkill):
    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(MycroftHomescreen, self).__init__(name="MycroftHomescreen")
        self.skill_manager = None
        self.notifications_model = []
        self.notifications_storage_model = []
        self.def_wallpaper_folder = path.dirname(__file__) + '/ui/wallpapers/'
        self.loc_wallpaper_folder = self.file_system.path + '/wallpapers/'
        self.selected_wallpaper = self.settings.get("wallpaper", "default.png")
        self.wallpaper_collection = []
        self.display_time = None
        self.display_date = None

    @property
    def platform(self):
        """Get the platform identifier string

        Returns:
            str: Platform identifier, such as "mycroft_mark_1",
                 "mycroft_picroft", "mycroft_mark_2".  None for non-standard.
        """
        if self.config_core and self.config_core.get("enclosure"):
            return self.config_core["enclosure"].get("platform")
        else:
            return None

    def initialize(self):
        self.skill_manager = SkillManager(self.bus)
        self._schedule_clock_update()
        self._schedule_date_update()
        self._schedule_weather_request()
        self._query_active_alarms()

        # Handler Registeration For Notifications
        self.add_event("homescreen.notification.set", self.handle_display_notification)
        self.add_event("homescreen.wallpaper.set", self.handle_set_wallpaper)
        self.add_event("skill.alarm.active-queried", self.handle_alarm_status)
        self.add_event("skill.alarm.scheduled", self.handle_alarm_status)
        self.add_event("skill.weather.local-forecast-obtained",
                       self.handle_local_forecast_response)
        self.gui.register_handler("homescreen.notification.set",
                                  self.handle_display_notification)
        self.gui.register_handler("homescreen.notification.pop.clear",
                                  self.handle_clear_notification_data)
        self.gui.register_handler("homescreen.notification.pop.clear.delete",
                                  self.handle_clear_delete_notification_data)
        self.gui.register_handler("homescreen.notification.storage.clear",
                                  self.handle_clear_notification_storage)
        self.gui.register_handler("homescreen.notification.storage.item.rm",
                                  self.handle_clear_notification_storage_item)

        if not self.file_system.exists("wallpapers"):
            os.mkdir(path.join(self.file_system.path, "wallpapers"))

        self.collect_wallpapers()

    def _schedule_clock_update(self):
        """Check for a clock update every ten seconds; start on a minute boundary."""
        clock_update_start_time = datetime.now().replace(second=0, microsecond=0)
        clock_update_start_time += timedelta(minutes=1)
        self.schedule_repeating_event(
            self.update_clock, when=clock_update_start_time, frequency=TEN_SECONDS
        )

    def _schedule_date_update(self):
        """Check for a date update every minute; start on a minute boundary."""
        date_update_start_time = datetime.now().replace(second=0, microsecond=0)
        date_update_start_time += timedelta(minutes=1)
        self.schedule_repeating_event(
            self.update_date, when=date_update_start_time, frequency=ONE_MINUTE
        )

    def _schedule_weather_request(self):
        """Check for a weather update every fifteen minutes."""
        self.schedule_repeating_event(
            self.request_weather, when=datetime.now(), frequency=FIFTEEN_MINUTES
        )

    def request_weather(self):
        """Emits a command over the message bus to get the local weather forecast."""
        command = Message("skill.weather.request-local-forecast")
        self.bus.emit(command)

    def _query_active_alarms(self):
        """Emits a command over the message bus query for active alarms."""
        command = Message("skill.alarm.query-active")
        self.bus.emit(command)

    def handle_local_forecast_response(self, event: Message):
        """Use the weather data from the event to populate the weather on the screen."""
        self.gui["homeScreenTemperature"] = event.data["temperature"]
        self.gui["homeScreenWeatherCondition"] = event.data["weather_condition"]

    def handle_alarm_status(self, event: Message):
        """Use the alarm data from the event to control visibility of the alarm icon."""
        self.gui["showAlarmIcon"] = event.data["active_alarms"]

    #####################################################################
    # Homescreen Registeration & Handling

    @resting_screen_handler("Mycroft Homescreen")
    def handle_idle(self, _):
        self.log.debug('Activating Time/Date resting page')
        self.update_clock()
        self.update_date()
        self.gui['buildDate'] = self.build_info.get('build_date', '')
        self.gui['wallpaper_path'] = self.check_wallpaper_path(self.selected_wallpaper)
        self.gui['selected_wallpaper'] = self.selected_wallpaper
        self.gui['notification'] = {}
        self.gui["notification_model"] = {
            "storedmodel": self.notifications_storage_model,
            "count": len(self.notifications_storage_model),
        }
        if self.platform == MARK_II:
            page = "mark_ii_idle.qml"
        else:
            page = "scalable_idle.qml"
        self.gui.show_page(page)

    #####################################################################
    # Build Info

    @property
    def build_info(self):
        """The /etc/mycroft/build-info.json file as a Dict."""
        data = {}
        filename = "/etc/mycroft/build-info.json"
        if (
            self.config_core["enclosure"].get("development_device")
            and Path(filename).is_file()
        ):
            with open(filename, "r") as build_info:
                data = json.loads(build_info.read())
        return data

    #####################################################################
    # Wallpaper Manager

    def collect_wallpapers(self):
        for dirname, dirnames, filenames in os.walk(self.def_wallpaper_folder):
            def_wallpaper_collection = filenames

        for dirname, dirnames, filenames in os.walk(self.loc_wallpaper_folder):
            loc_wallpaper_collection = filenames

        self.wallpaper_collection = def_wallpaper_collection + loc_wallpaper_collection

    @intent_file_handler("change.wallpaper.intent")
    def change_wallpaper(self, message):
        # Get Current Wallpaper idx
        current_idx = self.get_wallpaper_idx(self.selected_wallpaper)
        collection_length = len(self.wallpaper_collection) - 1
        if not current_idx == collection_length:
            fidx = current_idx + 1
            self.selected_wallpaper = self.wallpaper_collection[fidx]
            self.settings["wallpaper"] = self.wallpaper_collection[fidx]

        else:
            self.selected_wallpaper = self.wallpaper_collection[0]
            self.settings["wallpaper"] = self.wallpaper_collection[0]

        self.gui['wallpaper_path'] = self.check_wallpaper_path(self.selected_wallpaper)
        self.gui['selected_wallpaper'] = self.selected_wallpaper

    def get_wallpaper_idx(self, filename):
        try:
            index_element = self.wallpaper_collection.index(filename)
            return index_element
        except ValueError:
            return None

    def handle_set_wallpaper(self, message):
        image_url = message.data.get("url", "")
        now = datetime.datetime.now()
        setname = "wallpaper-" + now.strftime("%H%M%S") + ".jpg"
        if image_url:
            print(image_url)
            response = requests.get(image_url)
            with self.file_system.open(
                path.join("wallpapers", setname), "wb") as my_file:
                my_file.write(response.content)
                my_file.close()
            self.collect_wallpapers()
            cidx = self.get_wallpaper_idx(setname)
            self.selected_wallpaper = self.wallpaper_collection[cidx]
            self.settings["wallpaper"] = self.wallpaper_collection[cidx]

            self.gui['wallpaper_path'] = self.check_wallpaper_path(setname)
            self.gui['selected_wallpaper'] = self.selected_wallpaper

    def check_wallpaper_path(self, wallpaper):
        file_def_check = self.def_wallpaper_folder + wallpaper
        file_loc_check = self.loc_wallpaper_folder + wallpaper
        if path.exists(file_def_check):
            return self.def_wallpaper_folder
        elif path.exists(file_loc_check):
            return self.loc_wallpaper_folder

    #####################################################################
    # Manage notifications

    def handle_display_notification(self, message):
        """ Get Notification & Action """
        notification_message = {
            "sender": message.data.get("sender", ""),
            "text": message.data.get("text", ""),
            "action": message.data.get("action", ""),
            "type": message.data.get("type", ""),
        }
        if notification_message not in self.notifications_model:
            self.notifications_model.append(notification_message)
            self.gui["notifcation_counter"] = len(self.notifications_model)
            self.gui["notification"] = notification_message
            time.sleep(2)
            self.bus.emit(Message("homescreen.notification.show"))

    def handle_clear_notification_data(self, message):
        """ Clear Pop Notification """
        notification_data = message.data.get("notification", "")
        self.notifications_storage_model.append(notification_data)
        for i in range(len(self.notifications_model)):
            if (
                self.notifications_model[i]["sender"] == notification_data["sender"]
                and self.notifications_model[i]["text"] == notification_data["text"]
            ):
                if not len(self.notifications_model) > 0:
                    del self.notifications_model[i]
                    self.notifications_model = []
                else:
                    del self.notifications_model[i]
                break

        self.gui["notification_model"] = {
            "storedmodel": self.notifications_storage_model,
            "count": len(self.notifications_storage_model),
        }
        self.gui["notification"] = {}

    def handle_clear_delete_notification_data(self, message):
        """ Clear Pop Notification & Delete Notification Data """
        notification_data = message.data.get("notification", "")
        for i in range(len(self.notifications_model)):
            if (
                self.notifications_model[i]["sender"] == notification_data["sender"]
                and self.notifications_model[i]["text"] == notification_data["text"]
            ):
                if not len(self.notifications_model) > 0:
                    del self.notifications_model[i]
                    self.notifications_model = []
                else:
                    del self.notifications_model[i]
                break

    def handle_clear_notification_storage(self, _):
        """ Clear All Notification Storage Model """
        self.notifications_storage_model = []
        self.gui["notification_model"] = {
            "storedmodel": self.notifications_storage_model,
            "count": len(self.notifications_storage_model),
        }

    def handle_clear_notification_storage_item(self, message):
        """ Clear Single Item From Notification Storage Model """
        notification_data = message.data.get("notification", "")
        for i in range(len(self.notifications_storage_model)):
            if (
                self.notifications_storage_model[i]["sender"]
                == notification_data["sender"]
                and self.notifications_storage_model[i]["text"]
                == notification_data["text"]
            ):
                self.notifications_storage_model.pop(i)
                self.gui["notification_model"] = {
                    "storedmodel": self.notifications_storage_model,
                    "count": len(self.notifications_storage_model),
                }

    def update_date(self):
        """Formats the datetime object returned from the parser for display purposes."""
        formatted_date = nice_date(now_local())
        if self.display_date != formatted_date:
            self.display_date = formatted_date
            self._set_gui_date()

    def _set_gui_date(self):
        """Uses the data from the date skill to build the date as seen on the screen."""
        date_parts = self.display_date.split(", ")
        day_of_week = date_parts[0].title()
        month_day = date_parts[1].split()
        month = month_day[0][:3].title()
        day_of_month = now_local().strftime("%-d")
        gui_date = [day_of_week]
        if self.config_core.get("date_format") == "MDY":
            gui_date.extend([month, day_of_month])
        else:
            gui_date.extend([day_of_month, month])

        self.gui["homeScreenDate"] = " ".join(gui_date)

    def update_clock(self):
        """Broadcast the current local time in HH:MM format over the message bus.

        Provides a single place that determines the current local time and broadcasts
        it in the user-defined format (12 vs. 24 hour) for a clock implementation.
        """
        format_time_24_hour = self.config_core.get("time_format") == "full"
        formatted_time = nice_time(
            now_local(), speech=False, use_24hour=format_time_24_hour
        )
        if self.display_time != formatted_time:
            self.display_time = formatted_time
            self.gui["homeScreenTime"] = self.display_time

    def stop(self):
        pass


def create_skill():
    return MycroftHomescreen()
