# Eyegrade: grading multiple choice questions with a webcam
# Copyright (C) 2012 Jesus Arias Fisteus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#

#from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import (QImage, QWidget, QMainWindow, QPainter,
                         QSizePolicy, QApplication, QVBoxLayout,
                         QLabel, QIcon, QAction, QMenu,)

from PyQt4.QtCore import Qt, QTimer

from eyegrade.utils import resource_path


class ActionsManager(object):
    """Creates and manages the toolbar buttons."""

    _actions_grading_data = [
        ('snapshot', 'snapshot.svg', 'Sna&pshot'),
        ('manual_detect', 'manual_detect.svg', '&Manual bounds'),
        ('next_id', 'next_id.svg', '&Next student id'),
        ('edit_id', 'edit_id.svg', '&Edit student id'),
        ('save', 'save.svg', '&Save capture'),
        ('discard', 'discard.svg', '&Discard capture'),
        ]

    _actions_session_data = [
        ('new', 'new.svg', '&New session'),
        ('open', 'open.svg', '&Open session'),
        ('close', 'close.svg', '&Close session'),
        ('*separator*', None, None),
        ('exit', 'exit.svg', '&Exit'),
        ]

    _actions_help_data = [
        ('about', None, '&About'),
        ]

    def __init__(self, window):
        """Creates a manager for the given toolbar object."""
        self.window = window
        self.menubar = window.menuBar()
        self.toolbar = window.addToolBar('Grade Toolbar')
        self.menus = {}
        self.actions_grading = {}
        self.actions_session = {}
        action_lists = {'session': [], 'grading': []}
        for key, icon, tooltip in ActionsManager._actions_session_data:
            self._add_action(key, icon, tooltip, self.actions_session,
                             action_lists['session'])
        for key, icon, tooltip in ActionsManager._actions_grading_data:
            self._add_action(key, icon, tooltip, self.actions_grading,
                             action_lists['grading'])
        self._populate_menubar(action_lists)
        self._populate_toolbar(action_lists)

    def set_search_mode(self):
        self.actions_grading['snapshot'].setEnabled(True)
        self.actions_grading['manual_detect'].setEnabled(True)
        self.actions_grading['next_id'].setEnabled(False)
        self.actions_grading['edit_id'].setEnabled(False)
        self.actions_grading['save'].setEnabled(False)
        self.actions_grading['discard'].setEnabled(False)
        self.actions_session['close'].setEnabled(True)
        self.menus['grading'].setEnabled(True)

    def set_review_mode(self):
        self.actions_grading['snapshot'].setEnabled(False)
        self.actions_grading['manual_detect'].setEnabled(False)
        self.actions_grading['next_id'].setEnabled(True)
        self.actions_grading['edit_id'].setEnabled(True)
        self.actions_grading['save'].setEnabled(True)
        self.actions_grading['discard'].setEnabled(True)
        self.actions_session['close'].setEnabled(True)
        self.menus['grading'].setEnabled(True)

    def set_session_closed_mode(self):
        for key in self.actions_grading:
            self.actions_grading[key].setEnabled(False)
        self.menus['grading'].setEnabled(False)

    def _add_action(self, action_name, icon_file, tooltip, group, actions_list):
        action = self._create_action(action_name, icon_file, tooltip)
        if not action.isSeparator():
            group[action_name] = action
        actions_list.append(action)

    def _populate_menu(self, menu, actions_data):
        for key, icon, tooltip in actions_data:
            menu.addAction(self._create_action(key, icon, tooltip))

    def _create_action(self, action_name, icon_file, tooltip):
        if action_name == '*separator*':
            action = QAction(self.window)
            action.setSeparator(True)
        else:
            if icon_file:
                action = QAction(QIcon(resource_path(icon_file)),
                                 tooltip, self.window)
            else:
                action = QAction(tooltip, self.window)
        return action

    def _populate_menubar(self, action_lists):
        self.menus['session'] = QMenu('&Session', self.menubar)
        self.menus['grading'] = QMenu('&Grading', self.menubar)
        self.menubar.addMenu(self.menus['session'])
        self.menubar.addMenu(self.menus['grading'])
        for action in action_lists['session']:
            self.menus['session'].addAction(action)
        for action in action_lists['grading']:
            self.menus['grading'].addAction(action)
        help_menu = QMenu('&Help', self.menubar)
        self.menubar.addMenu(help_menu)
        self._populate_menu(help_menu, ActionsManager._actions_help_data)

    def _populate_toolbar(self, action_lists):
        for action in action_lists['grading']:
            self.toolbar.addAction(action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actions_session['close'])


class CamView(QWidget):
    def __init__(self, parent=None):
        super(CamView, self).__init__(parent)
        self.image = QImage(640, 480, QImage.Format_RGB888)
        self.image.fill(Qt.darkBlue)
        self.setFixedSize(640, 480)
#        self.cam = cv.CaptureFromCAM(0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image)

    def new_frame(self):
        self._capture_image()
        self.update()

    ## def _capture_image(self):
    ##     cvimage = cv.QueryFrame(self.cam)
    ##     self.image = QImage(cvimage.tostring(),
    ##                         cvimage.width, cvimage.height,
    ##                         QImage.Format_RGB888).rgbSwapped()


class CenterView(QWidget):
    def __init__(self, parent=None):
        super(CenterView, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.camview = CamView(parent=self)
        self.label_up = QLabel(('<img src="%s" height="16" width="16"> 5 '
                                '<img src="%s" height="16" width="16"> 7 '
                                '<img src="%s" height="16" width="16"> 3')\
                               %(resource_path('correct.svg'),
                                 resource_path('incorrect.svg'),
                                 resource_path('unanswered.svg')))
        self.label_down = QLabel('Test 2')
        layout.addWidget(self.camview)
        layout.addWidget(self.label_up)
        layout.addWidget(self.label_down)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(policy)
        self.center_view = CenterView()
        self.setCentralWidget(self.center_view)
        self.setWindowTitle("Test cam")
        self.actions_manager = ActionsManager(self)
        self.actions_manager.set_search_mode()
        self.adjustSize()
        self.setFixedSize(self.sizeHint())

        ## timer = QTimer(self)
        ## timer.timeout.connect(self.cam_view.new_frame)
        ## timer.setInterval(100)
        ## timer.start(500)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
