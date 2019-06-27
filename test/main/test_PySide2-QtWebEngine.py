import sys
from PySide2.QtWidgets import QMainWindow, QTabWidget, QTabBar
from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('My Browser')
        self.showMaximized()
    
        self.tab = QTabWidget()
        self.tab.setTabsClosable(True)
        self.setCentralWidget(self.tab)
        self.tab.tabCloseRequested.connect(self.tab.removeTab)
        self.load()

    def load(self):
        view = WebEngineView(self.tab)
        view.load(QUrl("https://www.baidu.com"))
        index = self.tab.addTab(view, "New Tab")
        self.tab.setCurrentIndex(index)


class WebEngineView(QWebEngineView):
    def __init__(self, tab):
        QWebEngineView.__init__(self, parent=tab)
        self.tab = self.parent()

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            view = WebEngineView(self.tab)
            index = self.tab.addTab(view, "New Tab")
            self.tab.setCurrentIndex(index)
            return view
        return QWebEngineView.createWindow(self, windowType)


if __name__ == "__main__":
    from PySide2.QtWidgets import QApplication
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())