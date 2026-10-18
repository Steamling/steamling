/*
    Steamling splash: the logo on the same field as the wallpaper, so
    splash -> desktop is one continuous surface.

    ksplashqml drives `stage` as startup progresses; stage 2 is "show yourself".
    Nothing here waits on a later stage, because Plasma Mobile's shell does not
    emit the full sequence - the unit's own exit is what takes the splash away.
*/
import QtQuick

Rectangle {
    id: root
    color: "#202126"

    property int stage

    onStageChanged: {
        if (stage == 2) {
            fadeIn.running = true;
        }
    }

    Image {
        id: logo
        anchors.centerIn: parent
        // rendered at 760x840; cap at half the screen's height so it holds its
        // proportions on any panel rather than being stretched to fit
        height: Math.min(420, parent.height * 0.5)
        fillMode: Image.PreserveAspectFit
        asynchronous: true
        smooth: true
        source: "images/logo.png"
        opacity: 0
    }

    OpacityAnimator {
        id: fadeIn
        target: logo
        from: 0
        to: 1
        duration: 400
        running: false
    }
}
