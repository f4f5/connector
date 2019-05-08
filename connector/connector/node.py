"""
node logic
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
        # return self.scores[self.scores.index(min(self.scores))]
        
        
            
        

    

def f(x):
    return x**x
        