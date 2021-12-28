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


try:
    # If IdleDisplaySkill exists then we assume that Mycroft-core 
    # has updated to the newer version and has a range of changes
    from mycroft.skills import IdleDisplaySkill
    from .skill.new_skill import HomescreenSkill
except ImportError:
    # If that class doesn't exist then we are on an old version of core.
    from .skill.old_skill import HomescreenSkill


def create_skill():
    """Boilerplate code to instantiate the skill."""
    return HomescreenSkill()
