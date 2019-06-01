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

class Node:
    def __init__(self):
        self.resource_mains = {}
        self.locations = {}
        self.server_types = {}
        self.remain_connections = {}
        self.scores = [] 
        self.load_config()
        self.pingter = new PyPing()
        self.ismainnode = False

    def load_config(self):
        serverConfig = {}
        with open('./config/server.json', encoding = 'utf8') as f:
            serverConfig = json.loads(f.read())
            self.server_type = serverConfig.get('server_type') 
            self.port = serverConfig.get('port')
            self.ip = serverConfig.get('ip') 
            self.location = serverConfig.get('locations')            
            self.remain_connection = serverConfig.get('remain_connection')
            self.score = serverConfig.get('score')
            self.pc = local.parse_pc_str(serverConfig.get('pc'))
            self.build_self_node()

    def build_self_node(self):
        self.node = {}
        pass

    def connect_2_network(self, url):
        """
        A node first connect to the network
        Args:
            url:  The first connect node's url and port.
        Returns:
        """
        url = url + '/node_all_info'
        try:
            res = requests.post(url)
            js = res.json()
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
        
    def choose_best_mainnode(self):
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

        return best_ten

    def prepare_for_mainnode(self):
        """
        1. info all the other main node the preparation
        2. set the main node relate info of this point.
        3. set server prepare for node connction
        """
        self.ismainnode = True
        

        pass

    def main_node_res(self):
        """RECEIVE INFO
        response to all the main nodes relate info if this node is a main node, includes:
            node update info 
            main node update info
        """
        pass
    
    def node_res(self):
        """RECEIVE INFO
        """
        pass
    
    def update_main_node(self):
        """SEND INFO

        exchange infomation from other main node.
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
            