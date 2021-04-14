import sys, time, _thread, os, subprocess, shutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal
from windows import Ui_Form

# ===== 默认参数 =======

pot_dir = 'C:\\"Program Files"\DAUM\PotPlayer\PotPlayerMini64.exe '
work_dir = ''
status_flag = 0  # ==(0 = 暂停,1 = 运行)
updata_flag = 0
quit_flag = 0
now_dir = '这里会显示正在播放的文件目录信息'
now_name = ''
now_number = 0
file_list = []
file_list_number = 0


class MainWindow(QWidget, Ui_Form):
    # 定义点击信号
    chooseSignal = pyqtSignal(str)

    def __init__(self, parent=None):
        global control_data, status_flag
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('片库管理助手 V1.0')
        # ==/ Icon设置 /===
        # self.setWindowIcon(QIcon('icon/256x256.ico'))
        # ==/ 按键信号设置 /================
        self.bt_start.clicked.connect(lambda: self.start())
        self.bt_stop.clicked.connect(lambda: self.stop())
        self.bt_zantin.clicked.connect(lambda: self.zantin())
        self.bt_skip.clicked.connect(lambda: self.save())
        self.bt_continue.clicked.connect(lambda: self.conntinue())
        self.bt_del_dir.clicked.connect(lambda: self.del_dir())
        self.bt_del_dir_1.clicked.connect(lambda: self.del_dir_1())
        self.bt_del_dir_2.clicked.connect(lambda: self.del_dir_2())
        self.bt_del_name.clicked.connect(lambda: self.delete())
        self.bt_set_potdir.clicked.connect(lambda: self.set_potdir())
        self.bt_set_workdir.clicked.connect(lambda: self.set_workdir())
        self.bt_skip_number.clicked.connect(lambda: self.skip())

        # ==/ 界面初始化 /==========
        self.show_potdir.setText(pot_dir)
        # 界面更新
        _thread.start_new_thread(lambda: self.flash(), ())

    def flash(self):  # ==/ 页面刷新函数 /====
        global updata_flag
        i = 0
        while True:
            time.sleep(0.2)
            while updata_flag == 1:
                updata_flag = 0
                i = i + 1
                # ===/ 更新控件 /=================================
                self.show_potdir.setText(pot_dir)
                self.show_workdir.setText(work_dir)
                self.show_video_dir.append(now_dir)
                self.show_video_dir.moveCursor(self.show_video_dir.textCursor().End)
                self.show_now_number.setText(str(now_number))
                self.show_files_number.setText(str(file_list_number))

    def set_potdir(self):
        global pot_dir, updata_flag
        a = QFileDialog.getOpenFileName(self)
        pot_dir = a[0]
        updata_flag = 1

    def set_workdir(self):
        global work_dir, updata_flag
        work_dir = QFileDialog.getExistingDirectory(self)
        self.findfiles()
        updata_flag = 1

    def findfiles(self):
        global work_dir, file_list, file_list_number
        many = 0
        for root, dirs, files in os.walk(work_dir):
            for name in files:
                filename = os.path.join(root, name)
                if str(filename[-3:]) == 'mp4' or str(filename[-3:]) == 'mkv' or str(filename[-3:]) == 'avi':
                    file_list.append(filename)
                    many = many + 1
            else:
                continue
        file_list_number = many
        print(file_list)
        print(file_list_number)

    def play(self):
        global status_flag, quit_flag, now_dir, updata_flag, file_list, now_number, file_list_number
        now_number = 0
        while status_flag == 1:
            while len(file_list) != 0 and status_flag == 1 and quit_flag != 1:
                now_dir = file_list[0]
                now_number = now_number + 1
                updata_flag = 1
                self.openPotplayer(now_dir)
                while True:
                    if quit_flag == 0:
                        break
                    else:
                        time.sleep(0.05)
                print(len(file_list))
                file_list = file_list[1:]
            time.sleep(0.1)
        now_number = 0
        file_list_number = 0
        updata_flag = 1
        status_flag = 0
        quit_flag = 0

    def conntinue(self):
        global quit_flag
        quit_flag = 0

    def skip(self):
        global file_list, now_number, updata_flag
        self.zantin()
        num = self.spinBox_skip_number.text()
        file_list = file_list[int(num):]
        now_number = int(now_number) + int(num)
        updata_flag = 1
        self.conntinue()

    def save(self):
        self.killedPotplayer(0)

    def stop(self):
        global status_flag
        status_flag = 0
        self.killedPotplayer(0)

    def zantin(self):
        global quit_flag
        quit_flag = 1
        self.killedPotplayer(1)

    def start(self):
        global status_flag, quit_flag
        # self.findfiles()
        status_flag = 1
        quit_flag = 0
        _thread.start_new_thread(lambda: self.play(), ())

    def openPotplayer(self, filename):
        global work_dir, qiut_flag
        print(pot_dir + filename)
        subprocess.call(pot_dir + filename, shell=True)
        qiut_flag = 0

    def killedPotplayer(self, mm):
        global quit_flag
        subprocess.call('taskkill /f /im PotPlayerMini64.exe', shell=True)
        if mm != 1:
            quit_flag = 0
        else:
            quit_flag = 1
        print(quit_flag)

    def delete(self):
        global now_name, quit_flag
        now_name = now_dir[now_dir.rfind('\\') + 1:]
        now_file_dir = now_dir[:now_dir.rfind('\\')]
        del_list = []
        for name in os.listdir(now_file_dir):
            if name.find(now_name[1:-4]) != -1:
                del_list.append(name)
                # os.remove(str(now_file_dir) + '/' + str(name))
        reply = QMessageBox.warning(self, '删除提示', '这些文件将会被删除：\n' + str(del_list) + '\n请确认',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for name in del_list:
                self.killedPotplayer(1)
                os.remove(str(now_file_dir) + '/' + str(name))
        else:
            QMessageBox.information(self, '删除提示', '删除操作已经取消')
        quit_flag = 0

    def del_dir(self):
        global now_name, quit_flag
        print(now_dir)
        now_flie_dir = now_dir[:now_dir.rfind('\\')]
        print(now_flie_dir)
        reply = QMessageBox.warning(self, '删除提示', '该文件夹将会被删除：\n' + now_flie_dir + '\n请确认',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.killedPotplayer(1)
            time.sleep(0.1)
            try:
                shutil.rmtree(now_flie_dir)
            except:
                QMessageBox.warning(self, '删除提示', '该文件夹删除：\n' + now_flie_dir + '\n删除失败，请确认状态')
        else:
            QMessageBox.information(self, '删除提示', '删除操作已经取消')
        quit_flag = 0

    def del_dir_1(self):
        global now_name, quit_flag
        now_flie_dir = now_dir[:now_dir.rfind('\\')]
        now_flie_dir = now_flie_dir[:now_flie_dir.rfind('/')]
        reply = QMessageBox.warning(self, '删除提示', '该文件夹将会被删除：\n' + now_flie_dir + '\n请确认',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.killedPotplayer(1)
            time.sleep(0.1)
            try:
                shutil.rmtree(now_flie_dir)
            except:
                QMessageBox.warning(self, '删除提示', '该文件夹删除：\n' + now_flie_dir + '\n删除失败，请确认状态')
        else:
            QMessageBox.information(self, '删除提示', '删除操作已经取消')
        quit_flag = 0

    def del_dir_2(self):
        global now_name, quit_flag
        now_flie_dir = now_dir[:now_dir.rfind('\\')]
        now_flie_dir = now_flie_dir[:now_flie_dir.rfind('/')]
        now_flie_dir = now_flie_dir[:now_flie_dir.rfind('/')]
        reply = QMessageBox.warning(self, '删除提示', '该文件夹将会被删除：\n' + now_flie_dir + '\n请确认',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.killedPotplayer(1)
            time.sleep(0.1)
            try:
                shutil.rmtree(now_flie_dir)
            except:
                QMessageBox.warning(self, '删除提示', '该文件夹删除：\n' + now_flie_dir + '\n删除失败，请确认状态')
        else:
            QMessageBox.information(self, '删除提示', '删除操作已经取消')
        quit_flag = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ma = MainWindow()
    ma.show()
    sys.exit(app.exec_())
