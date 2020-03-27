# -*- coding:UTF-8 -*-
# AUTHOR: Mki

# DESCRIPTION:  聊天室客户端
from usermain import *
from login import *
from bidroom import *
import threading
from socket import socket, AF_INET, SOCK_DGRAM
import json
import time
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog

class Client():
    def __init__(self,localAddr,serverAddr):
        '''
        初始化
        '''
        self.exitflag = 0
        self.addr = localAddr
        self.serverAddr = serverAddr
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(localAddr)
        self.auth = {}
        self.queue = []
        self.roomList = {}
        self.userList = {}
        self.specroom_id = 0
        self.roomID = 1
        self.notice = ''

        t = threading.Thread(target=self.start)
        #print('thread was born.......')
        t.setDaemon(True)
        t.start()

    def login(self):
        '''
        用户登陆
        '''
        msg = {}
        msg["auth"] = self.auth
        msg["type"] = "notice"
        self.send(msg)
        user_ui.show()

    def receive(self):
        '''
        接收消息
        '''
        while True:
            msg,addr = self.sock.recvfrom(8192)
            # #print(type(msg))
            # #print(msg)
            msg = json.loads(msg)
            self.handle(msg)
            # msg = str(msg,encoding="utf-8")
            # self.queue.append(msg)
            # self.chatWindow()

    def handle(self,msg):
        # #print(msg)
        if msg["type"] == "text":
            self.notice = msg["text"]
            # #print(text)
        elif msg["type"] == "roomList":
            self.roomList = msg["roomList"]
            self.userList = msg["userList"]
            self.roomID = msg["roomID"]

    #传入对象
    def send(self,msg):
        if len(self.auth) > 0:
            msg["auth"] = self.auth
            msg = json.dumps(msg)
            msg = bytes(msg, encoding='utf-8')
            self.sock.sendto(msg, self.serverAddr)

    def getList(self):
        while True:
            time.sleep(1)
            msg = {}
            msg["type"] = "List"
            self.send(msg)
            # #print(msg)

    def enterRoom(self):
        msg = {}
        msg["type"] = "auction"
        msg["rmID"] = str(self.specroom_id)
        # #print(self.roomList)
        self.send(msg)

    def leaveRoom(self):
        msg = {}
        msg["type"] = "leave"
        msg["rmID"] = str(self.specroom_id)
        self.specroom_id = 0
        self.send(msg)

    def yourprice(self,price):
        msg = {}
        msg["type"] = "price"
        msg["price"] = price
        msg["rmID"] = str(self.specroom_id)

        room = self.roomList[str(self.specroom_id)]
        room['highest'] = price
        self.userList[self.auth['name']]["givenprice"] = price
        self.send(msg)

    def privatemsg(self,num,text):
        msg = {}
        msg["type"] = "talk"
        msg["toWho"] = num
        msg["rmID"] = self.specroom_id
        msg["text"] = text
        self.send(msg)

    def ifleaveroom(self):
        try:
            if self.auth['name'] == self.roomList[str(self.specroom_id)]['highestbuyer']:
                return False
            return True
        except:
            return True

    def start(self):
        t = threading.Thread(target=self.receive)
        t.setDaemon(True)
        t.start()

        t = threading.Thread(target=self.getList)
        t.setDaemon(True)
        t.start()

class loginWindow(QMainWindow):
    def __init__(self):
        QDialog.__init__(self)
        self.login_ui=Ui_login()
        self.login_ui.setupUi(self,client,user_ui)

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '本程序',
                                               "Are you sure？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class userWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.user_ui=Ui_Usermain()
        self.user_ui.setupUi(self,client,bid_ui)

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '本程序',
                                               "Are you sure？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class bidWindow(QMainWindow):
    def __init__(self):
        QDialog.__init__(self)
        self.bid_ui=Ui_bidroom()
        self.bid_ui.setupUi(self,client)

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '本程序',
                                               "确认退出该竞拍室？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if client.ifleaveroom():
                client.leaveRoom()
                event.accept()
            else:
                event.ignore()
                client.notice = '[system] Sorry.You are likely to be the final buyer now. You cannot leave.'
        else:
            event.ignore()


if __name__ == "__main__":
    localHost = '127.0.0.1'
    localPort = 2227
    localAddr = (localHost,int(localPort))

    romoteHost = '127.0.0.1'
    romotePort = '8093'
    romoteAddr = (romoteHost,int(romotePort))
    while True:
        try:
            client = Client(localAddr,romoteAddr)
            break
        except:
            localPort = localPort+1
            localAddr = (localHost,int(localPort))

    app = QtWidgets.QApplication(sys.argv)
    bid_ui = bidWindow()
    user_ui = userWindow()  
    login_ui = loginWindow()

    login_ui.show()

    # user_ui.show()
    sys.exit(app.exec_())

