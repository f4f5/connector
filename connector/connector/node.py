"""
node logic
author: kdsjkjgaksdgjqawe@outlook.com
"""
import requests
from ping import PyPing
import psutil
from multiprocessing import Pool
import time
import speedtest
import random
import json
import local
from netio import ClientStream
from netio import server

class Node:
    def __init__(self):
        self.resource_mains = {}
        self.locations = {}
        self.server_types = {}
        self.remain_connections = {}
        self.scores = []   #ips 
        self.load_config()
        self.pingter = PyPing()
        self.ismainnode = False
        self.client = ClientStream()
        self.sever = SeverStream()        

    def load_config(self):
        serverConfig = {}
        with open('./config/server.json', encoding = 'utf8') as f:
            serverConfig = json.loads(f.read())
            self.server_type = serverConfig.get('server_type') 
            self.ip = serverConfig.get('ip') 
            self.location = serverConfig.get('locations')            
            self.remain_connection = serverConfig.get('remain_connection')
            self.score = serverConfig.get('score')
            self.pc = local.parse_pc_str(serverConfig.get('pc'))
            self.build_self_node()

    def build_self_node(self):
        self.node = {}
        pass

    async def connect_2_network(self, url):
        """
        A node first connect to the network
        
        Args:
            url:  The first connect node's url and port.            
        Returns:
        """        
        try:
            await client.handler(url)
            js = await client.requests({'op':'get_all_basic'})
            pass
        except Exception as e:
            print("connect to network exception!")
            print(e)
            return
        self.resource_mains = js.resource_mains
        self.locations = js.locations
        self.server_types = js.server_types
        self.remain_connections = js.remain_connections
        self.scores = js.scores

        if len(self.scores) < 100:
            self.scores.push(self.ip)
            self.prepare_for_mainnode()
            return
        else:
            mainnode = self.choose_best_mainnode()
            self.node['father'] = mainnode
            self.resource_mains[self.ip] = self.node
            
        
    def choose_best_mainnode(self): #选择前100个综合性能最好的节点作为主节点
        """
        choose the best ten ips to be the main node

        Returns:
            ip: string
        """
        if len(self.scores) < 100:
            return
        pingtime = []        
        for n in self.scores:
            pingtime.push(self.pingter.wrap_ping(n))
        pingorg = pingtime.copy()
        pingtime.sort()
        best_ten=[]
        for i in range(10):
            if(i>=len(pingtime)): break
            ind = pingorg.index(pingtime[i])
            best_ten.push(self.scores[ind])

        best = best_ten[0]
        for ip in best_ten:
            if(self.resource_mains[ip].remain_connections > self.resource_mains[best].remain_connections):
                best = ip
            
        return best

    def prepare_for_mainnode(self):  #准备成为主节点
        """
        1. info all the other main node the preparation
        2. set the main node relate info of this point.
        3. set server prepare for node connction

        ————————
        1. 通知其他节点该节点将成为主节点
        2. 设置相关参数
        3. 准备迎接主节点连接
        """
        self.ismainnode = True
                

        pass

    async def main_node_server(self):
        """
        Server as a main node to receive and process message. This function can be thought
        to be controller in MVC moudel. 

        ---------
        节点为主节点时的服务器，该函数有点像MVC模型里的控制器
        """
        data = await self.sever.reader.read()
        resp = {
            'get_all_basic':        self.resp_basic,  #just response the basic info
            'main_node_fail':       self.main_node_fail,    #just receive the info and do something
            '_main_node_fail':      self.main_node_fail_process,  #indicate the first main node to langch a main_node_fail info.
            'delete_node':          self.delete_node,
            'add_node':             self.add_node,
            'search_node':          self.search_node,
            'update_node':          self.update_node,
            'recieve_new_node':     self.recieve_new_node
        }

        pass
    
    async def node_server(self):
        """
        Server as a normal node to receive and process message. This function can be thought 
        to be controller in MVC moudel.

        ---------
        节点为常规节点时的服务器，该函数有点像MVC模型里的控制器
        """
        data = await self.sever.reader.read()
        resp = {
            'get_all_basic':        self.resp_basic,
            'change_main_node':     self.change_main_node,
            'delete_node':          self.delete_node,
            'add_node':             self.add_node,
            'search_node':          self.search_node,
            'update_node':          self.update_node
        }
        pass
    

    async def notify(self, data, toips):
        for ip in toips:            
            self.client.handler(ip)
            self.client.writer.write(data)
            await self.client.close_writer()


    def update_main_node(self):
        """SEND INFO

        exchange infomation from other main node.
        ——————————
        若为主节点身份 对网络做出更新（发送更新信息）
        """

        pass

    def update_node(self):
        """SEND INFO

        """
        if self.ismainnode:
            return self.update_main_node()

        pass
    
    def periodic_do(self):
        self.update_node()
        self.check_child_heartbeat()

        pass

    def check_child_heartbeat(self):
        if not ismainnode:
            return

        pass

    def delete_main_node(self):

        pass
    def delete_node(self):
        pass

    def select_new_main_node(self):
        """
        1 if ismainnode, select the best node of its child and send info to all the other mainnode
        
        """
        pass
            