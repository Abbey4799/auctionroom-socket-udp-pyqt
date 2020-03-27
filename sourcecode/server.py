# -*- coding:UTF-8 -*-

# DESCRIPTION:   聊天室服务器
from server_room import *
from specificroom import *
import threading
import time
from  socket import socket, AF_INET, SOCK_DGRAM
import logging
import json
import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QLabel

# logFormat = "%(asctime)s - %(levelname)s - %(message)s"
# logging.basicConfig(level=logging.INFO,format=logFormat,filename="test.log",filemode="a")


class Server():
    def __init__(self,address):
        '''
        initialize the server
        '''
        #Thread as Clock
        t1 = threading.Thread(target=self.refresh_time)
        t1.setDaemon(True)
        t1.start()

        self.addr = address
        self.bidderID = 1
        self.roomID = 1
        self.userList = {}
        self.roomList = {}
        self.bidroom = {}
        self.specroom_id = 0
        self.start()
        self.sysmsg = ''

    def initroomuser(self,num):
        users = self.roomList[str(num)]['buyers']
        for user in users:
            pp = self.userList[user]						
            pp["room"] = -1									#正处的竞拍室（只能有一个）
            pp["givenprice"] = -1							#目前喊价								#得到的竞拍物品



    #close the bidroom
    def closeroom(self,msg,num):
        try:
            if self.roomList[str(num)]['time'] == 0:
                self.allocate(num)
            time.sleep(2)
            self.initroomuser(num)
            self.roomList[str(num)]['highest'] = 'unstarted'
            self.roomList[str(num)]['highestbuyer'] = 'unstarted'
            self.roomList.pop(str(num))
            self.boardcast(msg)
        except:
            self.sysmsg = '[System] The room does not exist'

    #Clock for this system
    def refresh_time(self):
        while True:
            try:
                time.sleep(1)
                for room in self.roomList:
                    self.roomList[room]['time'] = self.roomList[room]['time'] - 1
                    if self.roomList[room]['time'] == 0:
                        msg = "Sorry!  Time is up"
                        self.closeroom(msg,room)
            except:
               pass

    #open a bidroom
    def openauction(self,price):
        room = {}
        room['buyersnum'] = 0
        room['price'] = price
        room['time'] = 200
        room['highest'] = 'unstarted'
        room['highestbuyer'] = 'unstarted'
        room['buyers'] = []
        self.roomList[str(self.roomID)] = room
        #print("You have opened room " + str(self.roomID) + " successfully")
        self.roomID = self.roomID + 1
        #print("The price is " + price + " dollars")

    #send NOTICE for all user
    def bulletin(self):
        msg = input("enter your NOTICE:")
        text = msg
        self.boardcast(text)

    #receive msg from clients
    def start(self):
        '''
        服务器开始接收消息
        '''
        #print('[*]srever start')

        #此处需要多线程，否则会无法渲染ui
        t = threading.Thread(target=self.recieve)
        #print('thread was born.......')
        t.setDaemon(True)
        t.start()

    #Send msg
    def send(self,msg,addr):
        '''
        发送消息
        '''
        s = socket(AF_INET, SOCK_DGRAM)
        # #print(type(msg))
        # #print(msg)
        s.sendto(msg, addr)

    #add client
    def addUser(self,auth,addr):
        '''
        添加用户
        '''
        self.userList[auth["name"]] = {}
        self.userList[auth["name"]]["addr"] = addr
        self.userList[auth["name"]]["pwd"] = auth["pwd"]
        self.userList[auth["name"]]["room"] = -1
        self.userList[auth["name"]]["bidderID"] = str(self.bidderID)
        self.userList[auth["name"]]["givenprice"] = -1
        self.userList[auth["name"]]["owing"]= []
        self.userList[auth["name"]]["mark"]= 0
        self.bidderID = self.bidderID+1

    #when a client enter room
    def enterroom(self,rmID,auth,addr):
        if self.userList[auth["name"]]["room"] > -1:
            text = ("Sorry, you have entered the room" + str(self.userList[auth["name"]]["room"]))
            self.solo(text,addr)
            return 
        if rmID == self.roomID or rmID > self.roomID:
            text = ("Sorry, the room doesn't exist.")
            self.solo(text,addr)
            return 
        self.userList[auth["name"]]["room"] = rmID
        room = self.roomList[str(rmID)]
        room['buyers'].append(auth["name"])
        room['buyersnum'] = room['buyersnum']+1
        #print(room['buyers'])
        msg1 = self.userList[auth['name']]['bidderID'] + '号 '+ auth['name'] + ' has been entered this room' 
        self.boardcastroom(msg1,rmID)


        # #print(room['buyersnum'])
        return

    #record the final owner of the good
    #two conditions:
    #1. Administrator closed the room
    #2. Time is up
    def allocate(self,rmID):
        # #print(rmID)
        try:
            if self.roomList[str(rmID)]['highestbuyer'] != 'unstarted':
                user = self.roomList[str(rmID)]['highestbuyer']
                self.userList[user]['owing'].append(rmID)
                self.userList[user]['mark'] = self.userList[user]['mark'] + int(self.roomList[str(rmID)]['highest'])
                msg = 'Good '+ str(rmID) + ' now belongs to '+ user + ' as '+ self.roomList[str(rmID)]['highest'] + ' dollars'
                self.boardcastroom(msg,str(rmID))
        except:
            return

    #when a client leave a room or being kicked out
    def leaveroom(self,rmID,auth,addr):
        try:
            text = '[system] ' + auth['name'] + ' has left the room.'
            room = self.roomList[str(rmID)]
            room['buyers'].remove(auth["name"])
            room['buyersnum'] = room['buyersnum'] - 1
            self.userList[auth['name']]['givenprice'] = -1
            self.userList[auth['name']]['room'] = -1
            self.renewhighest(str(rmID))
            self.boardcastroom(text,rmID)
        except:
            return
        
    #Check if the username is available
    def auth(self,auth,addr):
        '''
        用户权限认证
        '''
        if auth["name"] not in self.userList:
            self.addUser(auth,addr)
            return True
        else:
            if auth["pwd"] == self.userList[auth["name"]]["pwd"]:
                return True
            else:
                return False
    
    #pack msg
    def pack(self,msg):
        msg = json.dumps(msg)
        msg = bytes(msg, encoding='utf-8')
        return msg

    #send msg privately
    def solo(self,text,addr,username=''):
        '''
        私聊消息发送    
        '''
        msg = {}
        msg["type"] = "text"
        if username in self.userList:
            addr = self.userList[username]["addr"]
            #print(f"secret message to {username} ")
            msg["text"] = text
            msg = self.pack(msg)
            self.send(msg,addr)
        else:
            #print(f"secret message 'send failed'")
            msg["text"] = text
            msg = self.pack(msg)
            self.send(msg,addr)

    #broadcast the msg for all users
    def boardcast(self,text):
        '''
        群聊消息发送
        '''
        msg = {}
        msg["type"] = "text"
        msg["text"] = '[system] ' + text
        msg = self.pack(msg)
        for user in self.userList:
            #print(f"boardcast message :{str(text)} ")
            self.send(msg,self.userList[user]["addr"])

     #broadcast the msg for users in certain room
    def boardcastroom(self,text,rmID):
        msg = {}
        msg["type"] = "text"
        msg["text"] = '[system] ' + text
        msg = self.pack(msg)
        room = self.roomList[str(rmID)]
        for user in room['buyers']:
            self.send(msg,self.userList[user]["addr"])

    #send certain info to every client
    def sendList(self,msg,addr):
        msg = {}
        msg["type"] = "roomList"
        msg["roomList"] = self.roomList
        msg["userList"] = self.userList
        msg["roomID"] = self.roomID
        msg = self.pack(msg)
        self.send(msg,addr)

    #when a client call a price
    def yourprice(self,auth,price,bidroom):
        room = self.roomList[bidroom]
        room['highest'] = price
        room['highestbuyer'] = auth['name']
        msg = auth['name'] + ' has called ' + str(price) + ' dollars'
        self.boardcastroom(msg,bidroom)
        self.userList[auth['name']]['givenprice'] = price

    #handler for operation from client
    def handle(self,msg,addr):
        '''
        消息接收处理器
        '''
        if self.auth(msg["auth"],addr):
            if msg["type"]=="notice":
                text = (self.userList[msg["auth"]["name"]]["bidderID"] + "号 "+msg["auth"]["name"]+" " + "上线")
                self.boardcast(text)
            elif msg["type"]=="auction":
                text = '[+]enter new auction\n'
                rmID = int(msg["rmID"])
                self.enterroom(rmID,msg["auth"],addr)
            elif msg["type"]=="leave":
                rmID = int(msg["rmID"])
                self.leaveroom(rmID,msg["auth"],addr)
                # self.renewhighest(rmID)    
            elif msg["type"]=="List":
                self.sendList(msg,addr)
            elif msg["type"]=="price":
                auth = msg["auth"]
                price = msg["price"]
                bidroom = msg["rmID"]
                self.yourprice(auth,price,bidroom)
            elif msg["type"] == "talk":
                auth = msg["auth"]
                toWho = msg["toWho"]
                rmID = msg["rmID"]
                text = msg["text"]
                self.privatetalk(toWho,text,rmID,auth)
            else:
                pass
        else:
            text = ("Login failed")
            self.solo(text,addr)

    #receive msg from clients
    def recieve(self):
        '''
        接收消息
        '''
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(localaddr)
        while True:
            msg, addr = sock.recvfrom(8192)
            # #print(type(msg))
            # #print(msg)
            msg = json.loads(msg)
            self.handle(msg,addr)

    #check if the user is in this room
    def if_user_this_room(self,to_id,rmid):
        '''
        判断该用户是否在这间竞拍室中
        '''       
        room = self.roomList[str(rmid)]
        for name in room['buyers']:
            if self.userList[name]['bidderID'] == to_id:
                return name
        name = ""
        return name

    #snd private msg for certain user 
    def privatemsg(self,num,msg):
        name = self.if_user_this_room(num,self.specroom_id)
        if  name == "":
            self.sysmsg = "[system] This user is not in this room"
            return
        else:
            addr = self.userList[name]['addr']
            msg = '[private] Administrator: ' + msg
            self.solo(msg,addr)
    #handler for one user's private msg for another user 
    def privatetalk(self,toWho,text,rmid,auth):
        name = self.if_user_this_room(toWho,rmid)
        if name == "":
            addr = self.userList[auth['name']]['addr']
            msg = "[system] This user is not in this room"
            self.solo(msg,addr)
            return
        else:
            addr = self.userList[name]['addr']
            msg = '[private] ' + auth['name'] + ' says: ' + text
            self.solo(msg,addr)       

    #renew the highest bidder(unused in fact)
    def renewhighest(self,roomid):
        max = 0
        maxuser = 'unstarted'
        for user in self.roomList[str(roomid)]['buyers']:
            price = self.userList[user]['givenprice']
            if price != 'unstarted':
                if int(price) > max:
                    max = int(price)
                    maxuser = user
        if max == 0:
            max = 'unstarted'
        self.roomList[str(roomid)]['highest'] = max
        self.roomList[str(roomid)]['highestbuyer'] = maxuser

    #kick a certain buyer
    def kickbuyer(self,id):
        name = self.if_user_this_room(id,self.specroom_id)
        if  name == "":
            #print("the user isn't in this room")
            return
        else:
            room = self.roomList[str(self.specroom_id)]
            room['buyers'].remove(name)
            room['buyersnum'] = int(room['buyersnum']) - 1
            addr = self.userList[name]['addr']
            msg = "[System]You have been kicked out from this room."   
            msg1 = self.userList[name]['bidderID'] + '号 '+ name + ' has been kicked out from room' + str(self.specroom_id)
            self.solo(msg,addr)
            self.boardcastroom(msg1,self.specroom_id)
            self.renewhighest(self.specroom_id)



class roomWindow(QMainWindow):
    def __init__(self):
        QDialog.__init__(self)
        self.room_ui=Ui_room()
        self.room_ui.setupUi(self,server,specroom_ui)

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

class specWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.spec_ui=Ui_specificroom()
        self.spec_ui.setupUi(self,server)

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
    



if __name__ == '__main__':
    # localhost = sys.argv[1]
    # localport = sys.argv[2]
    localhost = '127.0.0.1'
    localport = '8093'
    localaddr = (localhost,int(localport))
    # Server(localaddr)

    #create a server
    server = Server(localaddr)

    app = QtWidgets.QApplication(sys.argv)
    specroom_ui = specWindow()
    room_ui = roomWindow()
    #connect

    #show
    room_ui.show()
    sys.exit(app.exec_())




