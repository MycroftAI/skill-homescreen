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
"""Wallpaper management for the home screen."""
from datetime import datetime
from pathlib import Path

DEFAULT_WALLPAPER = "nasa.png"


class Wallpaper:
    """
    Attributes:
        collection: a list of paths to wallpaper files found on the device
        default: the default wallpaper as defined in the skill settings
        selected: the currently active (selected) wallpaper
        skill_directory: the wallpaper directory in the home screen skill
        user_directory: a directory on the device for storing user-defined wallpapers
    """

    def __init__(self, skill_root_dir: str, skill_data_dir: str, default: str):
        self.skill_directory = Path(skill_root_dir).joinpath("ui/wallpapers")
        self.user_directory = Path(skill_data_dir).joinpath("wallpapers")
        self._ensure_user_directory_exists()
        self.default = self._get_file_path(default)
        self.selected = self.default
        self.collection = []
        self.collect()

    def _ensure_user_directory_exists(self):
        """Ensures the directory for user-defined wallpapers exists."""
        if not self.user_directory.exists():
            self.user_directory.mkdir()

    def collect(self):
        """Builds a list of wallpapers provided by the skill and added by the user."""
        for wallpaper_path in self.skill_directory.iterdir():
            self.collection.append(wallpaper_path)
        for wallpaper_path in self.user_directory.iterdir():
            self.collection.append(wallpaper_path)

    def change(self):
        """Selects the next wallpaper in the collection for display.

        Starts over the beginning of the list after the last in the collection.  If
        the "selected" attribute contains a value not in the collection, the default
        is selected.
        """
        if self.selected in self.collection:
            if self.selected == self.collection[-1]:
                self.selected = self.collection[0]
            else:
                index_of_selected = self.collection.index(self.selected)
                self.selected = self.collection[index_of_selected + 1]
        else:
            self.selected = self.default

    def add(self, image):
        """Adds a new wallpaper to the collection and selects it for display."""
        file_name = "wallpaper-" + datetime.now().strftime("%H%M%S") + ".jpg"
        file_path = self.user_directory.joinpath(file_name)
        with open(file_path, "wb") as wallpaper_file:
            wallpaper_file.write(image)
        self.collection.append(file_path)
        self.selected = file_path

    def _get_file_path(self, file_name: str):
        """Determines if a wallpaper file name is from the user or skill directory."""
        skill_path = self.skill_directory.joinpath(file_name)
        user_path = self.user_directory.joinpath(file_name)
        if skill_path.exists():
            file_path = skill_path
        else:
            file_path = user_path

        return file_path