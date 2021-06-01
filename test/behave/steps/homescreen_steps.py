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
#
import time

from behave import given, then

from mycroft.messagebus import Message
from test.integrationtests.voight_kampff import emit_utterance, mycroft_responses, then_wait


def wait_for_message(context, message_type):
    """Common method for detecting Skill specific notify messages"""
    msg_type = 'skill.homescreen.notify.{}'.format(message_type)
    def check_for_msg(message):
        return (message.msg_type == msg_type, '')

    passed, debug = then_wait(msg_type, check_for_msg, context)

    if not passed:
        debug += mycroft_responses(context)
    if not debug:
        debug = "Mycroft didn't emit {} message".format(message_type)

    assert passed, debug

@then('the wallpaper should be changed')
def then_wallpaper_changed(context):
    wait_for_message(context, 'wallpaper_changed')
