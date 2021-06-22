import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Mycroft.CardDelegate {
    id: idleRoot
    skillBackgroundColorOverlay: "transparent"
    cardBackgroundOverlayColor: "transparent"
    cardRadius: 0
    skillBackgroundSource: Qt.resolvedUrl(sessionData.wallpaper_path + sessionData.selected_wallpaper)
    property bool horizontalMode: idleRoot.width > idleRoot.height ? 1 : 0
    readonly property color primaryBorderColor: Qt.rgba(1, 0, 0, 0.9)
    readonly property color secondaryBorderColor: Qt.rgba(1, 1, 1, 0.7)
    property real dropSpread: 0.3
    property real dropRadius: 8
    property real dropSample: 8
    property color dropColor: Qt.rgba(0.2, 0.2, 0.2, 0.60)

    property int notificationCounter: sessionData.notifcation_counter
    property var notificationData: sessionData.notification
    property var notificationModel: sessionData.notification_model
    signal clearNotificationSessionData

    onNotificationDataChanged: {
        console.log("Notification Should Have Changed")
        if(sessionData.notification.text && sessionData.notification !== "") {
            display_notification()
        }
    }

    onNotificationModelChanged: {
        if(notificationModel.count > 0) {
            notificationsStorageView.model = sessionData.notification_model.storedmodel
        } else {
            notificationsStorageView.model = sessionData.notification_model.storedmodel
            notificationsStorageView.forceLayout()
            if(notificationsStorageViewBox.opened) {
                notificationsStorageViewBox.close()
            }
        }
    }

    Connections {
        target: idleRoot
        onClearNotificationSessionData: {
            triggerGuiEvent("homescreen.notification.pop.clear", {"notification": idleRoot.notificationData})
        }
    }

    function display_notification() {
        console.log("Notification Counter Changed")
        console.log(notificationData)
        if(idleRoot.notificationData !== undefined) {
            console.log("Got A Notification")
            if(idleRoot.notificationData.type == "sticky"){
                console.log("Got Sticky Type")
                var component = Qt.createComponent("NotificationPopSticky.qml");
            } else {
                console.log("Got Other Type")
                var component = Qt.createComponent("NotificationPopTransient.qml");
            }
            if (component.status != Component.Ready)
            {
                if (component.status == Component.Error) {
                    console.debug("Error: "+ component.errorString());
                }
                return;
            } else {
                var notif_object = component.createObject(notificationPopupLayout, {currentNotification: idleRoot.notificationData})
            }
        } else {
            console.log(idleRoot.notificationData)
        }
    }
    
    Item {
        anchors.fill: parent

        RowLayout {
            id: weatherItemBox
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.round(parent.width * 0.1969)
            height: Math.round(parent.height * 0.2150)
            spacing: Mycroft.Units.gridUnit

            Kirigami.Icon {
                id: weatherItemIcon
                source: Qt.resolvedUrl("icons/sun.svg")
                Layout.preferredWidth: Mycroft.Units.gridUnit * 3
                Layout.preferredHeight: Mycroft.Units.gridUnit * 3
                visible: false
                layer.enabled: true
                layer.effect: DropShadow {
                    spread: idleRoot.dropSpread
                    radius: idleRoot.dropRadius
                    color:  idleRoot.dropColor
                }
            }

            Text {
                id: weatherItem
                text: "50°"
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignRight | Qt.AlignTop
                fontSizeMode: Text.Fit;
                minimumPixelSize: 50;
                font.pixelSize: parent.height;
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                color: "white"
                visible: false
                layer.enabled: true
                layer.effect: DropShadow {
                    spread: idleRoot.dropSpread
                    radius: idleRoot.dropRadius
                    color:  idleRoot.dropColor
                }
            }
        }

        Item {
            id: timeItemBox
            anchors.top: parent.top
            anchors.topMargin: Math.round(parent.height * 0.10)
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.round(parent.width * 0.70)
            height: Math.round(parent.height * 0.6565)

            Text {
                id: timeItem
                anchors.fill: parent
                text: sessionData.time_string.replace(":", "꞉")
                fontSizeMode: Text.Fit;
                font.bold: true;
                minimumPixelSize: 50;
                font.pixelSize: parent.height;
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                color: "white"
                layer.enabled: true
                layer.effect: DropShadow {
                    spread: idleRoot.dropSpread
                    radius: idleRoot.dropRadius
                    color:  idleRoot.dropColor
                }
            }
        }

        Item {
            id: dateItemBox
            anchors.top: timeItemBox.bottom
            anchors.topMargin: -Math.round(height * 0.40)
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.round(parent.width * 0.6065)
            height: Math.round(parent.height * 0.1950)

            Text {
                id: dateItem
                anchors.fill: parent
                text: sessionData.weekday_string + " " + sessionData.month_string.substring(0,3) + " " + sessionData.day_string
                fontSizeMode: Text.Fit;
                minimumPixelSize: 50;
                font.pixelSize: parent.height;
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                color: "white"
                layer.enabled: true
                layer.effect: DropShadow {
                    spread: idleRoot.dropSpread
                    radius: idleRoot.dropRadius
                    color:  idleRoot.dropColor
                }
            }
        }

        RowLayout {
            id: bottomItemBox
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            width: Math.round(parent.width * 0.1630)
            height: Mycroft.Units.gridUnit * 2
            spacing: Mycroft.Units.gridUnit * 2.75

            Kirigami.Icon {
                id: micItemIcon
                source: Qt.resolvedUrl("icons/mic.svg")
                Layout.preferredWidth: Mycroft.Units.gridUnit * 2
                Layout.preferredHeight: Mycroft.Units.gridUnit * 2
                color: "white"
                visible: false
                layer.enabled: true
                layer.effect: DropShadow {
                    spread: idleRoot.dropSpread
                    radius: idleRoot.dropRadius
                    color:  idleRoot.dropColor
                }
            }

            Kirigami.Icon {
                id: camItemIcon
                source: Qt.resolvedUrl("icons/cam.svg")
                width: Mycroft.Units.gridUnit * 3
                height: Mycroft.Units.gridUnit * 3
                color: "white"
                visible: false
                layer.enabled: true
                layer.effect: DropShadow {
                    spread: idleRoot.dropSpread
                    radius: idleRoot.dropRadius
                    color:  idleRoot.dropColor
                }
            }
        }

        Kirigami.Icon {
            id: widgetLeftTop
            anchors.left: parent.left
            anchors.top: parent.top
            source: Qt.resolvedUrl("icons/mic.svg")
            width: Mycroft.Units.gridUnit * 3
            height: Mycroft.Units.gridUnit * 3
            color: "white"
            visible: false
            layer.enabled: true
            layer.effect: DropShadow {
                spread: idleRoot.dropSpread
                radius: idleRoot.dropRadius
                color:  idleRoot.dropColor
            }
        }

        Kirigami.Icon {
            id: widgetLeftBottom
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            source: Qt.resolvedUrl("icons/mic.svg")
            width: Mycroft.Units.gridUnit * 3
            height: Mycroft.Units.gridUnit * 3
            color: "white"
            visible: false
            layer.enabled: true
            layer.effect: DropShadow {
                spread: idleRoot.dropSpread
                radius: idleRoot.dropRadius
                color:  idleRoot.dropColor
            }
        }

        Kirigami.Icon {
            id: widgetRightTop
            anchors.right: parent.right
            anchors.top: parent.top
            source: Qt.resolvedUrl("icons/mic.svg")
            width: Mycroft.Units.gridUnit * 3
            height: Mycroft.Units.gridUnit * 3
            color: "white"
            visible: false
            layer.enabled: true
            layer.effect: DropShadow {
                spread: idleRoot.dropSpread
                radius: idleRoot.dropRadius
                color:  idleRoot.dropColor
            }
        }

        Kirigami.Icon {
            id: widgetRightBottom
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            source: Qt.resolvedUrl("icons/notificationicon.svg")
            width: Mycroft.Units.gridUnit * 3
            height: Mycroft.Units.gridUnit * 3
            color: "white"
            visible: idleRoot.notificationModel.count > 0
            enabled: visible
            
            layer.enabled: true
            layer.effect: DropShadow {
                spread: idleRoot.dropSpread
                radius: idleRoot.dropRadius
                color:  idleRoot.dropColor
            }
            
            Rectangle {
                color: "red"
                anchors.centerIn: parent
                width: parent.width * 0.40
                height: parent.height * 0.40
                radius: width
                z: 10

                Label {
                    color: "white"
                    anchors.fill: parent
                    fontSizeMode: Text.Fit
                    minimumPixelSize: 2
                    font.pixelSize: height * 0.7
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignHCenter
                    text: idleRoot.notificationModel.count
                }
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    notificationsStorageViewBox.open()
                }
            }
        }
    }
    
    Label {
        id: buildDate
        visible: sessionData.build_date === "" ? 0 : 1
        enabled: sessionData.build_date === "" ? 0 : 1
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.bottomMargin: -Mycroft.Units.gridUnit * 2
        font.pixelSize: 22
        wrapMode: Text.WordWrap
        text: "BI " + sessionData.build_date
        color: "white"
        layer.enabled: true
        layer.effect: DropShadow {
            spread: idleRoot.dropSpread
            radius: idleRoot.dropRadius
            color:  idleRoot.dropColor
        }
    }

    Column {
        id: notificationPopupLayout
        anchors.fill: parent
        spacing: Kirigami.Units.largeSpacing * 4
        property int cellWidth: idleRoot.width
        property int cellHeight: idleRoot.height
        z: 9999
    }

    Popup {
        id: notificationsStorageViewBox
        width: parent.width * 0.80
        height: parent.height * 0.80
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        parent: idleRoot

        background: Rectangle {
            color: "transparent"
        }

        Row {
            id: topBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: parent.height * 0.20
            spacing: parent.width * 0.10

            Rectangle {
                width: parent.width * 0.50
                height: parent.height
                color: "#313131"
                radius: 10

                Kirigami.Heading {
                    level: 1
                    width: parent.width
                    anchors.left: parent.left
                    anchors.leftMargin: Kirigami.Units.largeSpacing
                    anchors.verticalCenter: parent.verticalCenter
                    text: "Notifications"
                    color: "#ffffff"
                }
            }

            Rectangle {
                width: parent.width * 0.40
                height: parent.height
                color: "#313131"
                radius: 10

                RowLayout {
                    anchors.centerIn: parent

                    Kirigami.Icon {
                        Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                        Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                        source: Qt.resolvedUrl("img/clear.svg")
                        color: "white"
                    }

                    Kirigami.Heading {
                        level: 3
                        width: parent.width
                        Layout.fillWidth: true
                        text: "Clear"
                        color: "#ffffff"
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        triggerGuiEvent("homescreen.notification.storage.clear", {})
                    }
                }
            }
        }

        ListView {
            id: notificationsStorageView
            anchors.top: topBar.bottom
            anchors.topMargin: Kirigami.Units.largeSpacing
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            clip: true
            highlightFollowsCurrentItem: false
            spacing: Kirigami.Units.smallSpacing
            property int cellHeight: notificationsStorageView.height
            delegate: NotificationDelegate{}
        }
    }
}
