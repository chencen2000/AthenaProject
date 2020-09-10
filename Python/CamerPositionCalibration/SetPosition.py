import requests
from PyQt5 import QtWidgets, QtGui
from Ui_SetPosition import Ui_Dialog

class SetPositionDlg(QtWidgets.QWidget, Ui_Dialog):
    def __init__(self, title='', position=0, parent=None):
        super(SetPositionDlg, self).__init__(parent)
        self.setupUi(self)
        self.pos = position
        if bool(title):
            self.label.setText(title)
        self.get_position()
        self.pushButton.clicked.connect(self.set_position)

    def set_position(self):   
        v = self.lineEditNew.text()
             
        try:
            # r = requests.get('http://localhost:8010/lift/setpos?p={}'.format(self.pos))
            r = requests.get('http://localhost:8010/lift/setpos', params={'p':self.pos})
            if r.status_code==200:
                if r.json()['status'] == 'OK':
                    v = r.json()['parse']['P{}'.format(self.pos)]
                    # self.labelValue.setText('P2={}'.format(v))
                    self.lineEditCurrent.setText(v)
        except:
            pass
        pass

    def get_position(self):
        try:
            # r = requests.get('http://localhost:8010/lift/position?p={}'.format(self.pos))
            r = requests.get('http://localhost:8010/lift/position', params={'p':self.pos})
            if r.status_code==200:
                if r.json()['status'] == 'OK':
                    v = r.json()['parse']['P{}'.format(self.pos)]
                    # self.labelValue.setText('P2={}'.format(v))
                    self.lineEditCurrent.setText(v)
        except:
            pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = SetPositionDlg("title set P2")
    w.show()
    sys.exit(app.exec_())    