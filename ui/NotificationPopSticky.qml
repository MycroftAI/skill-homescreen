import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    id: popbox
    color: "#313131"
    radius: 10
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.leftMargin: Kirigami.Units.largeSpacing
    anchors.rightMargin: Kirigami.Units.largeSpacing
    height: notificationRowBoxLayout.implicitHeight + (Kirigami.Units.gridUnit + Kirigami.Units.largeSpacing)
    property var currentNotification
    
    RowLayout {
        id: notificationRowBoxLayout
        anchors.fill: parent
        anchors.margins: Kirigami.Units.largeSpacing

        Column {
            id: notificationColumnBoxLayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Kirigami.Units.largeSpacing

            Label {
                id: notificationHeading
                text: currentNotification.sender
                width: parent.width
                elide: Text.ElideRight
                font.capitalization: Font.SmallCaps
                font.bold: true
                font.pixelSize: parent.width * 0.065
                color: "#ffffff"
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Mycroft.MycroftController.sendRequest(currentNotification.action, {})
                    }
                }
            }

            Kirigami.Separator {
                width: parent.width
                height: Kirigami.Units.smallSpacing * 0.25
                color: "#8F8F8F"
            }

            Label {
                id: notificationContent
                text: currentNotification.text
                width: parent.width
                wrapMode: Text.WordWrap
                font.pixelSize: parent.width * 0.045
                maximumLineCount: 2
                elide: Text.ElideRight
                color: "#ffffff"
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Mycroft.MycroftController.sendRequest(currentNotification.action, {})
                    }
                }
            }
        }

        Kirigami.Separator {
            Layout.preferredWidth: Kirigami.Units.smallSpacing * 0.25
            Layout.fillHeight: true
            color: "#8F8F8F"
        }
        
        Item {
            Layout.minimumWidth: parent.width * 0.15
            Layout.fillHeight: true

            AbstractButton {
                width: parent.width - Kirigami.Units.largeSpacing * 2
                height: width
                anchors.centerIn: parent

                background: Rectangle {
                    color: "transparent"
                }

                contentItem: Kirigami.Icon {
                    anchors.centerIn: parent
                    width: Kirigami.Units.iconSizes.medium
                    height: width
                    source: Qt.resolvedUrl("icons/close.svg")
                }

                onClicked: {
                    triggerGuiEvent("homescreen.notification.pop.clear.delete", {"notification": currentNotification})
                    popbox.destroy()
                }
            }
        }
    }
} 
