// Copyright 2021 Mycroft AI Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
import QtQuick 2.12
import QtQuick.Controls 2.0
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Mycroft.CardDelegate {
    id: homeScreenRoot
    skillBackgroundColorOverlay: "transparent"
    cardBackgroundOverlayColor: "transparent"
    skillBackgroundSource: Qt.resolvedUrl(sessionData.wallpaper_path + sessionData.selected_wallpaper)

    HomeScreenImage {
        id: homeScreenWeatherCondition
        anchors.left: parent.left
        anchors.leftMargin: gridUnit * 18
        anchors.top: parent.top
        heightUnits: 3
        imageSource: sessionData.homeScreenWeatherCondition
        width: gridUnit * 3
    }

    HomeScreenLabel {
        id: homeScreenTemperature
        anchors.top: parent.top
        anchors.left: homeScreenWeatherCondition.right
        anchors.leftMargin: gridUnit
        fontSize: 59
        fontStyle: "Regular"
        heightUnits: 3
        text: sessionData.homeScreenTemperature + "°"
        width: gridUnit * 6
    }

    HomeScreenImage {
        id: homeScreenActiveAlarm
        anchors.right: parent.right
        anchors.top: parent.top
        heightUnits: 3
        imageSource: "icons/alarm.svg"
        visible: sessionData.showAlarmIcon
        width: gridUnit * 3
    }

    HomeScreenLabel {
        id: homeScreenBuildDate
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.leftMargin: gridUnit * 5
        fontSize: 22
        fontStyle: "Regular"
        heightUnits: 3
        text: sessionData.buildDate
        width: gridUnit * 10
    }

    HomeScreenLabel {
        id: homeScreenTime
        anchors.top: parent.top
        anchors.topMargin: gridUnit * 6
        fontSize: 200
        fontStyle: "Bold"
        heightUnits: 10
        text: sessionData.homeScreenTime.replace(":", "꞉")
        width: parent.width
    }

    HomeScreenLabel {
        id: homeScreenDate
        anchors.top: homeScreenTime.bottom
        anchors.topMargin: gridUnit * 3
        fontSize: 59
        fontStyle: "Regular"
        heightUnits: 3
        text: sessionData.homeScreenDate
        width: parent.width
    }
}
