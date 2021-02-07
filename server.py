import socket
import os
import sys
from _thread import *
import json

IP = '127.0.0.1'
PORT = 2221

#----------------------------------------------------------------------------------------------------------------#
class server:
    def fetch_data(self,filename):
        f = open(filename, "r")
        di = json.load(f)
        f.close()
        return di

    #----------------------------------------------------------------------------------------------------------------#

    def dump_data(self,filename, data):
        with open(filename, "w") as jsonFile:
            json.dump(data, jsonFile)

    #----------------------------------------------------------------------------------------------------------------#

    def get_userName(self,iport):
        UIPort = self.fetch_data("UIPort.txt") 
        for entry in UIPort:
            if UIPort[entry]==iport:
                return entry

	#----------------------------------------------------------------------------------------------------------------#

    def printUIPort(self):
        UIPort = self.fetch_data("UIPort.txt") 
        for entry in UIPort.keys():
            print(entry + " " + UIPort[entry])
            print

    #----------------------------------------------------------------------------------------------------------------#

    def isUserExist(self,userID , password):
        userData = self.fetch_data("userData.txt") 
        if userID in userData:
            return True
        return False

    #----------------------------------------------------------------------------------------------------------------#

    def isRollExist(self,roll):
        uroll = self.fetch_data("uroll.txt") 
        for r in uroll:
            if uroll[r]==roll:
                return True
        return False

	#----------------------------------------------------------------------------------------------------------------#

    def create_user(self,userID, password, roll, iport):
        if self.isUserExist(userID, password) == False:
            userData = self.fetch_data("userData.txt")

            if self.isRollExist(roll):
                return "This rollno already exist."
            
            userData[userID] = password   
            self.dump_data("userData.txt", userData)

            uroll = self.fetch_data("uroll.txt") 
            uroll[userID] = roll
            self.dump_data("uroll.txt", uroll)

            return "User created successfully."
        else:
            return "User already existed"

	#----------------------------------------------------------------------------------------------------------------#

    def login(self,userID, pwd, iport):
        userData = self.fetch_data("userData.txt") 
        if userID in userData.keys():
            if userData[userID] == pwd:
                UIPort = self.fetch_data("UIPort.txt") 
                UIPort[userID] = iport
                self.dump_data("UIPort.txt", UIPort)
                return "User login Successfully"
            else:
                return "Invalid password"
        else:
            return "User doesn't exist"    

	#----------------------------------------------------------------------------------------------------------------#

    def create_group(self,gname, iport):
        groups = self.fetch_data("groups.txt") 
        userName = self.get_userName(iport)
        if gname in groups:
            return "Group already exist"
        else:
            ls = []
            ls.append(userName)
            groups[gname] = ls
            self.dump_data("groups.txt", groups)
            return "Group created successfully."

	#----------------------------------------------------------------------------------------------------------------#

    def join_group(self,gname, iport):
        userName = self.get_userName(iport)
        groups = self.fetch_data("groups.txt") 
        if gname not in groups:
            return "Group doesn't exist."
        else:
            if userName in groups[gname]:
                return "You are already a member."
            groups[gname].append(userName)
            self.dump_data("groups.txt", groups)
            return "Group joined successfully."

	#----------------------------------------------------------------------------------------------------------------#

    def list_groups(self):
        resp = ""
        groups = self.fetch_data("groups.txt") 
        if len(groups)==0:
            return "No groups present"
        for entry in groups:
            resp += entry + " | "
        resp = resp[:-3]
        return resp

	#----------------------------------------------------------------------------------------------------------------#

	# Assumption :--> g1,g2,g2

    def getIPs(self,tokens):
        UIPort = self.fetch_data("UIPort.txt") 
        groups = self.fetch_data("groups.txt") 
        names = tokens[1].split(",")
        ips = "IP||"
        for name in names:
            if name in UIPort:
                ips += UIPort[name]+ "||"		
            elif name in groups.keys():
                for users in groups[name]:
                    uip = UIPort[users]
                    ips += uip + "||"
            else:
                return "Invalid User name or Group name."
        return ips

	#----------------------------------------------------------------------------------------------------------------#

    def process_request(self,msg):
        #print(msg) 
        tokens = msg.split(" ")
        iport = tokens[-1].replace(" ", "")
        tokens = tokens[:-1]
        # print(tokens)
        cmd = tokens[0]

        if(cmd=="CREATE_USER"):
            if len(tokens)!=4:
                return "Invalid Number of arguments."
            userId = tokens[1]
            pwd = tokens[2]
            roll = tokens[3]
            res = self.create_user(userId, pwd, roll, iport)
            return res
        if(cmd=="LOGIN"):
            if len(tokens)!=3:
                return "Invalid Number of arguments."        
            userId = tokens[1]
            pwd = tokens[2]
            res = self.login(userId, pwd, iport)
            return res

        if(cmd.lower()=="create"):
            if len(tokens)!=2:
                return "Invalid Number of arguments."
            gname = tokens[1]
            res = self.create_group(gname, iport)
            return res

        if(cmd=="JOIN"):
            if len(tokens)!=2:
                return "Invalid Number of arguments."
            gname = tokens[1]
            res = self.join_group(gname, iport)
            return res

        if(cmd=="LIST"):
            if len(tokens)!=1:
                return "Invalid Number of arguments."
            res = self.list_groups()
            return res

        if(cmd=="SEND"):
            res = self.getIPs(tokens)
            msg = ""
            for i in range(2, len(tokens)):
                msg+=tokens[i] + " "
            res += msg
            return res
        if(cmd=="CHECK"):
        #printUIPort()
            return "ALL TEST CASES PASS! WAHH BHAIMYA FUMLL CHECKUP BAZI"

        return "NO String Received.."

	#----------------------------------------------------------------------------------------------------------------#

    def threaded_client(self,connection):
        while True:
            data = connection.recv(2048).decode('utf-8')
            resp = self.process_request(data)
        #print(resp)
            if not data:
                break
            connection.sendall(str.encode(resp))
        connection.close()

	#----------------------------------------------------------------------------------------------------------------#

    def main(self):
        if len(sys.argv)!=2:
            print("Please enter correct no. of arguments")
            return
        global PORT
        PORT = int(sys.argv[1]) 

        ServerSocket = socket.socket()

        ServerSocket.bind((IP, PORT))

        print('Listening..')
        ServerSocket.listen(5)

        while True:
            Client, address = ServerSocket.accept()
            start_new_thread(self.threaded_client, (Client,))
        ServerSocket.close()
s1=server()
s1.main()
