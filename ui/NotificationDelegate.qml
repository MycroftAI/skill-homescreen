import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    id: delegate
    color: "#313131"
    radius: 10
    readonly property ListView listView: ListView.view
    width: listView.width
    height: notificationRowBoxLayout.implicitHeight + (Kirigami.Units.gridUnit + Kirigami.Units.largeSpacing)
    
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
                text: modelData.sender
                width: parent.width
                elide: Text.ElideRight
                font.capitalization: Font.SmallCaps
                font.bold: true
                font.pixelSize: parent.width * 0.060
                color: "#ffffff"
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Mycroft.MycroftController.sendRequest(modelData.action, {})
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
                text: modelData.text
                width: parent.width
                wrapMode: Text.WordWrap
                font.pixelSize: parent.width * 0.040
                maximumLineCount: 2
                elide: Text.ElideRight
                color: "#ffffff"
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        Mycroft.MycroftController.sendRequest(modelData.action, {})
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
                    source: Qt.resolvedUrl("icons/delete.svg")
                }

                onClicked: {
                    triggerGuiEvent("homescreen.notification.storage.item.rm", {"notification": modelData})
                    popbox.destroy()
                }
            }
        }
    }
} 
