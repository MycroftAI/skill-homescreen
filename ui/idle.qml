import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: idleRoot
    skillBackgroundColorOverlay: "transparent"
    skillBackgroundSource: Qt.resolvedUrl("wallpapers/" + sessionData.selected_wallpaper)
    property bool horizontalMode: idleRoot.width > idleRoot.height ? 1 : 0
    readonly property color primaryBorderColor: Qt.rgba(1, 0, 0, 0.9)
    readonly property color secondaryBorderColor: Qt.rgba(1, 1, 1, 0.7)
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

    AbstractButton {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: Kirigami.Units.iconSizes.large
        height: width
        visible: idleRoot.notificationModel.count > 0

        background: Rectangle {
            color: "#313131"
            border.width: 1
            border.color: "#8F8F8F"
            layer.enabled: true
            layer.effect: DropShadow {
                color: "#000000"
                radius: 10
                spread: 0.2
                samples: 16
            }
        }

        contentItem: Kirigami.Icon {
            width: Kirigami.Units.iconSizes.smallMedium
            height: Kirigami.Units.iconSizes.smallMedium
            source: Qt.resolvedUrl("img/notification-icon.svg")
        }

        onClicked: {
            notificationsStorageViewBox.open()
        }

        Rectangle {
            color: "red"
            anchors.right: parent.right
            anchors.rightMargin: -Kirigami.Units.largeSpacing * 0.50
            anchors.top: parent.top
            anchors.topMargin: -Kirigami.Units.largeSpacing * 0.50
            width: parent.width * 0.50
            height: parent.height * 0.50
            radius: width
            z: 10

            Label {
                color: "white"
                anchors.centerIn: parent
                text: idleRoot.notificationModel.count
            }
        }
    }

    ColumnLayout {
        id: grid
        anchors.fill: parent
        anchors.leftMargin: Kirigami.Units.largeSpacing * 2
        anchors.rightMargin: Kirigami.Units.largeSpacing * 2
        anchors.bottomMargin: Kirigami.Units.largeSpacing
        anchors.topMargin: Kirigami.Units.largeSpacing * 4 + Kirigami.Units.smallSpacing
        spacing: 0

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.fillHeight: true

            Label {
                id: time
                width: parent.width
                height: parent.height
                font.capitalization: Font.AllUppercase
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.family: "Noto Sans Display"
                font.weight: Font.Bold
                font.pixelSize: horizontalMode ? parent.height / 1 : parent.height / 1.5
                color: "white"
                text: sessionData.time_string.replace(":", "꞉")
                layer.enabled: true
                layer.effect: DropShadow {
                    color: "#000000"
                    radius: 10
                    spread: 0.2
                    samples: 16
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.minimumHeight: Kirigami.Units.largeSpacing + Kirigami.Units.smallSpacing
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.preferredHeight: weekday.contentHeight

            Label {
                id: weekday
                width: parent.width
                height: parent.height
                font.pixelSize: date.paintedHeight //horizontalMode ? parent.height / 2.5 : parent.height / 5
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignBottom
                wrapMode: Text.WordWrap
                font.family: "Noto Sans Display"
                font.weight: Font.DemiBold
                text: sessionData.weekday_string
                color: "white"
                layer.enabled: true
                layer.effect: DropShadow {
                    color: "#000000"
                    radius: 10
                    spread: 0.2
                    samples: 16
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.minimumHeight: Kirigami.Units.largeSpacing
        }

        Rectangle {
            color: "transparent"
            Layout.fillWidth: true
            Layout.fillHeight: true

            Label {
                id: date
                width: parent.width
                height: parent.height
                font.pixelSize: horizontalMode ? parent.height / 3 : parent.height / 5
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignTop
                wrapMode: Text.WordWrap
                font.family: "Noto Sans Display"
                font.weight: Font.DemiBold
                text: sessionData.month_string
                color: "white"
                layer.enabled: true
                layer.effect: DropShadow {
                    color: "#000000"
                    radius: 10
                    spread: 0.2
                    samples: 16
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
        anchors.margins: Kirigami.Units.largeSpacing
        font.pixelSize: 22
        wrapMode: Text.WordWrap
        font.family: "Noto Sans Display"
        text: "BI " + sessionData.build_date
        color: "white"
        layer.enabled: true
        layer.effect: DropShadow {
            verticalOffset: 2
            color: "#000000"
            radius: 5
            spread: 0.5
            samples: 16
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
