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
from os import path
from pathlib import Path

from mycroft.messagebus.message import Message
from mycroft.skills import MycroftSkill, resting_screen_handler, intent_handler
from mycroft.skills.skill_loader import load_skill_module
from mycroft.skills.skill_manager import SkillManager


class MycroftHomescreen(MycroftSkill):
    # The constructor of the skill, which calls MycroftSkill's constructor
    def __init__(self):
        super(MycroftHomescreen, self).__init__(name="MycroftHomescreen")
        self.skill_manager = None
        self.notifications_model = []
        self.notifications_storage_model = []
        self.wallpaper_folder = path.dirname(__file__) + '/ui/wallpapers/'
        self.selected_wallpaper = self.settings.get("wallpaper", "default.png")
        self.wallpaper_collection = []

    def initialize(self):
        now = datetime.datetime.now()
        callback_time = datetime.datetime(
            now.year, now.month, now.day, now.hour, now.minute
        ) + datetime.timedelta(seconds=60)
        self.schedule_repeating_event(self.update_dt, callback_time, 10)
        self.skill_manager = SkillManager(self.bus)

        # Handler Registeration For Notifications
        self.add_event("homescreen.notification.set",
                       self.handle_display_notification)
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
        
        self.collect_wallpapers()

        # Import Date Time Skill As Date Time Provider
        # TODO - replace with Skills API call in 21.02
        root_dir = self.root_dir.rsplit("/", 1)[0]
        try:
            time_date_path = str(root_dir) + "/mycroft-date-time.mycroftai/__init__.py"
            time_date_id = "datetimeskill"
            datetimeskill = load_skill_module(time_date_path, time_date_id)
            from datetimeskill import TimeSkill

            self.dt_skill = TimeSkill()
        except:
            self.log.info("Failed To Import DateTime Skill")

    #####################################################################
    # Homescreen Registeration & Handling

    @resting_screen_handler("Mycroft Homescreen")
    def handle_idle(self, _):
        self.log.debug('Activating Time/Date resting page')
        self.gui['time_string'] = self.dt_skill.get_display_current_time()
        self.gui['date_string'] = self.dt_skill.get_display_date()
        self.gui['weekday_string'] = self.dt_skill.get_weekday()
        self.gui['month_string'] = self.split_month_string(self.dt_skill.get_month_date())[1]
        self.gui['day_string'] = self.split_month_string(self.dt_skill.get_month_date())[0]
        self.gui['year_string'] = self.dt_skill.get_year()
        self.gui['build_date'] = self.build_info.get('build_date', '')
        self.gui['selected_wallpaper'] = self.selected_wallpaper
        self.gui['notification'] = {}
        self.gui["notification_model"] = {
            "storedmodel": self.notifications_storage_model,
            "count": len(self.notifications_storage_model),
        }
        self.gui.show_page("idle.qml")

    def handle_idle_update_time(self):
        self.gui["time_string"] = self.dt_skill.get_display_current_time()
        self.gui["date_string"] = self.dt_skill.get_display_date()
        self.gui["weekday_string"] = self.dt_skill.get_weekday()
        self.gui["month_string"] = self.split_month_string(self.dt_skill.get_month_date())[1]
        self.gui['day_string'] = self.split_month_string(self.dt_skill.get_month_date())[0]
        self.gui["year_string"] = self.dt_skill.get_year()

    def update_dt(self):
        self.gui["time_string"] = self.dt_skill.get_display_current_time()
        self.gui["date_string"] = self.dt_skill.get_display_date()
        self.gui["weekday_string"] = self.dt_skill.get_weekday()
        self.gui["month_string"] = self.split_month_string(self.dt_skill.get_month_date())[1]
        self.gui['day_string'] = self.split_month_string(self.dt_skill.get_month_date())[0]
        self.gui["year_string"] = self.dt_skill.get_year()
        
    def split_month_string(self, varstring):
        month_string = varstring.split(" ")
        if self.config_core.get('date_format') == 'MDY':
            day_string = month_string[1]
            month_string = month_string[0]
        else:
            day_string = month_string[0]
            month_string = month_string[1]

        return [day_string, month_string]

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
        for dirname, dirnames, filenames in os.walk(self.wallpaper_folder):
            self.wallpaper_collection = filenames

    @intent_handler("change.wallpaper.intent")
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

        self.gui['selected_wallpaper'] = self.selected_wallpaper

    def get_wallpaper_idx(self, filename):
        try:
            index_element = self.wallpaper_collection.index(filename)
            return index_element
        except ValueError:
            return None

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

    def stop(self):
        pass


def create_skill():
    return MycroftHomescreen()
