import sys
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFrame,
    QTextEdit,
    QPlainTextEdit,
    QSplitter,
    QStyleFactory,
    QApplication,
    QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QPixmap, QBrush


class Example(QWidget):

    def __init__(self, name, tags, text):
        self.app = QApplication(sys.argv)
        super().__init__()

        self.title = name

        self.initUI(name, tags, text)

    def initUI(self, name, tags, text):
        hbox = QHBoxLayout(self)

        topleft = QPlainTextEdit(tags)
        topleft.setFrameShape(QFrame.StyledPanel)

        #topright = QPlainTextEdit(tags)
        # topright.setFrameShape(QFrame.StyledPanel)

        topright = QLabel()
        print(name)
        pixmap = QPixmap("123.jpg")
        topright.setPixmap(pixmap)
        topright.show()

        bottom = QPlainTextEdit(text)
        bottom.setFrameShape(QFrame.StyledPanel)

        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topright)

        splitter3 = QSplitter(Qt.Vertical)
        splitter3.addWidget(splitter1)
        splitter3.addWidget(bottom)

        hbox.addWidget(splitter3)
        self.setLayout(hbox)

        self.setGeometry(200, 200, 500, 600)
        self.setWindowTitle(self.title)
        self.show()

    def onChanged(self, text):

        self.lbl.setText(text)
        self.lbl.adjustSize()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
