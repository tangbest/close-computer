#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QHeaderView, QTableWidgetItem, \
    QAbstractItemView, QProgressBar, QFileDialog, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt, QFile, QTimer, QDateTime
from PyQt5.QtGui import QPixmap,QPainter, QIcon, QPixmap
from PyQt5 import QtGui

import contextlib
import requests
import pprint
import re
import time
import subprocess

from public import tools_dlgbase
from widgets import ui_main
from public import tools_url
from public import tools_time

def openMainDlg():
    import sys
    app = QApplication(sys.argv)
    w = CMainDlg()
    sys.exit(app.exec_())

class CMainDlg(tools_dlgbase.CDlgBase, QMainWindow, ui_main.Ui_MainWindow):
    def __init__(self):
        super(CMainDlg, self).__init__()
        self.setupUi(self)
        self.Center()
        self.initData()
        self.initLayer()
        self.initEvent()
        self.show()

    def initData(self):
        self.m_oCurTimeTimer = QTimer()
        self.m_oCloseWindowTimer = QTimer()
        self.m_iCloseTime = 0
        self.m_bStartClose = False

    def initLayer(self):
        self.setFixedSize(self.width(), self.height())
        self.initStyle()
        self.setTuoPang()

    def setTuoPang(self):
        # 创建窗口托盘
        self.pTray = QSystemTrayIcon(self)
        # 设置托盘图标样式
        icon = QIcon()
        icon.addPixmap(QPixmap(":/res/icon.png"))
        self.pTray.setIcon(icon)
        # 显示图标
        self.pTray.show()

        quitAction = QAction("&退出吧", self, triggered=QApplication.instance().quit)  # 退出APP
        self.trayMenu = QMenu(self)
        self.trayMenu.addAction(quitAction)
        self.pTray.setContextMenu(self.trayMenu)
        self.pTray.setToolTip("关机软件")
        self.pTray.showMessage("提示", "开启关机定时器")
        self.pTray.messageClicked.connect(self.onTrayMessageClick)
        # #托盘图标被激活
        self.pTray.activated.connect(self.onTrayActivated)

    # 界面上关闭按钮
    def closeEvent(self, event):
        event.ignore()  # 忽略关闭事件
        self.hide()  # 隐藏窗体

    # 托盘图标事件
    def onTrayActivated(self, reason):
        print("触发托盘图标事件", reason)
        if reason == QSystemTrayIcon.DoubleClick:  # 双击事件
            self.onTrayDoubleClick()
        elif reason == QSystemTrayIcon.Trigger:  # 单击事件
            self.onTrayTrigger()

    def onTrayDoubleClick(self):
        print("双击了托盘")
        if self.isMinimized() or not self.isVisible():
            self.showNormal()  # 正常显示
            self.activateWindow()
        else:
            self.showMinimized()  # 最小化

    def onTrayTrigger(self):
        print("点击了托盘")

    def onTrayMessageClick(self, *args):
        print("点击了托盘信息")

    def initStyle(self):
        qss_file = QFile(":res/style.qss")
        qss_file.open(QFile.ReadOnly)
        qss = str(qss_file.readAll(), encoding='utf-8')
        qss_file.close()
        self.setStyleSheet(qss)

    @pyqtSlot()
    def on_pbDo_clicked(self):
        if self.m_bStartClose:
            self.cancelCloseWindow()
            return
        iSetHour = self.teSetTime.time().hour()
        iSetMin = self.teSetTime.time().minute()
        iYear, iMon, iDay, iHour, iMin, iSec = time.localtime()[:6]
        iDisTime = (iSetHour - iHour) * 3600 + (iSetMin - iMin) * 60 + (0 - iSec)
        if (iSetHour, iSetMin, iSec) <= (iHour, iMin, iSec):
            iCloseTime = iDisTime + 24*60*60
        else:
            iCloseTime = iDisTime
        self.m_iCloseTime = time.time() + iCloseTime
        print(time.time())
        print("剩余关闭时间", iCloseTime, tools_time.getHourMiniSecDes(iCloseTime))

        self.m_oCloseWindowTimer.timeout.connect(self.checkNeedClose)
        self.m_oCloseWindowTimer.start(1000)
        self.pbDo.setText("取消执行")
        self.m_bStartClose = True

    def cancelCloseWindow(self):
        self.m_bStartClose = False
        self.m_iCloseTime = 0
        self.m_oCloseWindowTimer.stop()
        self.pbDo.setText("执行")
        self.txtTip.setText("")

    def initEvent(self):
        self.m_oCurTimeTimer.timeout.connect(self.showCurTime)
        self.m_oCurTimeTimer.start(1000)

    def checkNeedClose(self):
        fCurTime = time.time()
        if fCurTime > self.m_iCloseTime:
            self.m_oCloseWindowTimer.stop()
            self.closeWindow()
        else:
            iLeftTime = int(self.m_iCloseTime - fCurTime)
            sTime = tools_time.getHourMiniSecDes(iLeftTime)
            self.txtTip.setText("{time}后关闭电脑".format(time=sTime))

    def closeWindow(self):
        print("关机了...")
        sCmd = "shutdown -s -t 1"
        subprocess.run(sCmd)

    def showCurTime(self):
        oTime = QDateTime.currentDateTime()
        sTime1 = oTime.toString("hh:mm:ss")
        sTime2 = oTime.toString("yyyy-MM-dd")
        sDay = oTime.toString("ddd")
        self.lbTime.setText(sTime1)
        sTime = "{year}({week})".format(year=sTime2, week=sDay)
        self.lbData.setText(sTime)






