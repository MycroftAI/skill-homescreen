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
"""Skill to display a home screen (a.k.a. idle screen) on a GUI enabled device."""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from mycroft.messagebus.message import Message
from mycroft.skills import MycroftSkill, resting_screen_handler, intent_file_handler
from mycroft.util.format import nice_time, nice_date
from mycroft.util.time import now_local
from .skill import DEFAULT_WALLPAPER, Wallpaper

FIFTEEN_MINUTES = 900
MARK_II = "mycroft_mark_2"
ONE_MINUTE = 60
TEN_SECONDS = 10


class HomescreenSkill(MycroftSkill):
    """Skill to display a home screen (a.k.a. idle screen) on a GUI enabled device.

    Attributes:
        display_date: the date string currently being displayed on the screen
        display_time: the time string currently being displayed on the screen
        wallpaper: An instance of the class for managing wallpapers.
    """

    def __init__(self):
        super().__init__(name="HomescreenSkill")
        self.display_time = None
        self.display_date = None
        self.wallpaper = Wallpaper(self.root_dir, self.file_system.path)
        self.settings_change_callback = self._handle_settings_change

    @property
    def platform(self) -> Optional[str]:
        """The platform from the device configuration (e.g. "mycroft_mark_1")

        Returns:
            Platform identifier if one is defined, otherwise None.
        """
        platform = None
        if self.config_core and self.config_core.get("enclosure"):
            platform = self.config_core["enclosure"].get("platform")

        return platform

    def _handle_settings_change(self):
        """Reacts to changes in the user settings for this skill."""
        self._init_wallpaper()

    def _set_wallpaper(self):
        wallpaper_file = self.settings.get("wallpaper_file", DEFAULT_WALLPAPER)
        wallpaper_url = self.settings.get("wallpaper_url", "")
        if wallpaper_file == "url":
            self.wallpaper.add(wallpaper_url)
            self.wallpaper.selected = wallpaper_url
        elif wallpaper_file != self.wallpaper.selected.name:
            self.wallpaper.change(wallpaper_file)

        self.gui["wallpaperPath"] = str(self.wallpaper.selected)
        log_msg = "Changed home screen wallpaper to "
        log_msg += wallpaper_url if wallpaper_file == "url" else wallpaper_file
        self.log.info(log_msg)

    def initialize(self):
        """Performs tasks after instantiation but before loading is complete."""
        self._init_wallpaper()
        self._add_event_handlers()
        self._schedule_clock_update()
        self._schedule_date_update()
        self._schedule_weather_request()
        self._query_active_alarms()

    def _init_wallpaper(self):
        if self.gui.connected:
            self._set_wallpaper()

    def _add_event_handlers(self):
        """Defines the events this skill will listen for and their handlers."""
        self.add_event("skill.alarm.query-active.response", self.handle_alarm_status)
        self.add_event("skill.alarm.scheduled", self.handle_alarm_status)
        self.add_event(
            "skill.weather.local-forecast-obtained", self.handle_local_forecast_response
        )

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

    @resting_screen_handler("Mycroft Homescreen")
    def handle_show_resting_screen(self, _):
        """Populates and shows the resting screen."""
        self.log.debug("Displaying the idle screen.")
        self.update_clock()
        self.update_date()
        self.set_build_date()
        if self.platform == MARK_II:
            page = "mark_ii_idle.qml"
        else:
            page = "scalable_idle.qml"
        self.gui.show_page(page)

    def set_build_date(self):
        """Sets the build date on the screen from a file, if it exists.

        The build date won't change without a reboot.  This only needs to occur once.
        """
        build_date = ""
        build_info_path = Path("/etc/mycroft/build-info.json")
        is_development_device = self.config_core["enclosure"].get("development_device")
        if is_development_device and build_info_path.is_file():
            with open(build_info_path) as build_info_file:
                build_info = json.loads(build_info_file.read())
                build_date = build_info.get("build_date", "")

        self.gui["buildDate"] = build_date

    @intent_file_handler("change.wallpaper.intent")
    def change_wallpaper(self, _):
        """Handles a user's request to change the wallpaper.

        Each time this intent is executed the next item in the list of collected
        wallpapers will be displayed and the skill setting will be updated.
        """
        self.wallpaper.next()
        self.settings["wallpaper"] = self.wallpaper.selected.name
        self.gui["wallpaperPath"] = str(self.wallpaper.selected)

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


def create_skill():
    """Boilerplate code to instantiate the skill."""
    return HomescreenSkill()
