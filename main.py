import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

import simpleaudio as sa


# https://stackoverflow.com/questions/25950049/creating-a-transparent-overlay-with-qt
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # https://stackoverflow.com/questions/17968267/how-to-make-click-through-windows-pyqt
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(QtCore.Qt.WA_NoChildEventsForParent, True)

        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowStaysOnTopHint |  # Puts the animation on top of everything
            QtCore.Qt.FramelessWindowHint |  # Removes the frame
            QtCore.Qt.X11BypassWindowManagerHint  # Make it fill the screen and not show up in the taskbar/dock
        )

        # Transparent background to draw over screen
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.geometry = QtWidgets.qApp.desktop().availableGeometry()

        self.height = self.geometry.height()
        self.width = self.geometry.width()

        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignLeft,
                QtCore.QSize(self.width, self.height),  # Fill screen
                QtWidgets.qApp.desktop().availableGeometry()
            ))

        # Move window to top left corner
        self.move(0, 0)

        # The width of the animation thing
        self.bar_width = 50
        # How far it gets to the bottom
        self.offset_from_bottom = int(self.height * 0.03)

        # https://www.learnpyqt.com/tutorials/qpropertyanimation/

        self.animationWidgets = {}

        self.animationWidgets["left"] = QtWidgets.QWidget(self)
        self.animationWidgets["right"] = QtWidgets.QWidget(self)

        self.animations = {}

        for anim_details in [{"name": "left_attach", "side": "left"}, {"name": "right_attach", "side": "right"}]:
            # Create a widget for ech animation
            # TODO: Hide widgets when not in use instead of moving off screen
            widget = self.animationWidgets[anim_details["side"]]

            # Create animations
            # TODO: Add comments here
            first_part = QtCore.QPropertyAnimation(widget, b"pos")
            if anim_details["side"] == "left":
                first_part.setEndValue(QtCore.QPoint(self.bar_width - 100, -self.offset_from_bottom))
            else:
                first_part.setEndValue(QtCore.QPoint(self.width - self.bar_width, -self.offset_from_bottom))
            first_part.setDuration(233)
            first_part.setEasingCurve(QtCore.QEasingCurve.OutCubic)

            second_part = QtCore.QPropertyAnimation(widget, b"pos")
            if anim_details["side"] == "left":
                second_part.setEndValue(QtCore.QPoint(-100, -self.offset_from_bottom))
            else:
                second_part.setEndValue(QtCore.QPoint(self.width, -self.offset_from_bottom))
            second_part.setDuration(1000)
            second_part.setEasingCurve(QtCore.QEasingCurve.OutCubic)

            anim_group = QtCore.QSequentialAnimationGroup()
            anim_group.addAnimation(first_part)
            anim_group.addAnimation(second_part)

            self.animations[anim_details["name"]] = anim_group

    def playAnimation(self, side, anim_name, colour):
        # Set styles
        self.animationWidgets[side].setStyleSheet("background-color: rgba(255, 255, 255, 50); border: 15px solid " +
                                                  colour + "; border-radius: 25px;")
        self.animationWidgets[side].resize(100, self.height)
        if side == "left":
            self.animationWidgets[side].move(self.bar_width - 100, -self.height)
        else:
            self.animationWidgets[side].move(self.width - self.bar_width, -self.height)

        # https://simpleaudio.readthedocs.io/en/latest/
        wave_obj = sa.WaveObject.from_wave_file("sounds/" + anim_name + ".wav")
        wave_obj.play()

        self.animations[anim_name].start()

    # Just test functions, not that clean
    def afterOneSecond(self):
        self.playAnimation("right", "right_attach", "rgb(239, 43, 41)")

    def afterThreeSeconds(self):
        self.playAnimation("left", "left_attach", "rgb(27, 202, 226)")

    def afterFiveSeconds(self):
        self.playAnimation("left", "left_attach", "rgb(27, 202, 226)")
        self.playAnimation("right", "right_attach", "rgb(239, 43, 41)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    # https://stackoverflow.com/questions/21897322/pyqt-application-load-complete-event
    t = QtCore.QTimer()
    t.singleShot(1000, mywindow.afterOneSecond)
    t.singleShot(3000, mywindow.afterThreeSeconds)
    t.singleShot(5000, mywindow.afterFiveSeconds)
    sys.exit(app.exec_())
