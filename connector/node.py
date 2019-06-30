"""
node logic
author: kdsjkjgaksdgjqawe@outlook.com
"""
from ping import PyPing
import psutil
import util
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
        self.sever = server       

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
            js = await self.requests({'op':'get_main_node'}, url)
            pass
        except Exception as e:
            print("connect to network exception!")
            print(e)
            return

        self.scores = js.scores

        if len(self.scores) < 100:            
            rs = await self.req_resource_file(random.choice(self.scores))            
            self.resource_mains = rs.resource_mains
            self.locations = rs.locations
            self.server_types = rs.server_types
            self.remain_connections = rs.remain_connections
            self.scores = rs.scores
            self.ismainnode = True   # indicate the server will be main node server.
            util.opush(self.scores,self.ip)
            await self.notify({
                    'op': 'new_main_node',
                    'node': self.node
                }, self.scores)
            return
        else:
            mainnode = self.choose_best_mainnode()
            self.node['father'] = mainnode
            self.mainnode = mainnode
            rs = await self.req_resource_file(mainnode)
            self.resource_mains = rs.resource_mains
            self.locations = rs.locations
            self.server_types = rs.server_types
            self.remain_connections = rs.remain_connections
            self.scores = rs.scores
            await self.notify({
                    'op': 'new_node',
                    'node': self.node
                }, mainnode)
            
        
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
    

    async def main_node_server(self):
        """
        Server as a main node to receive and process message. This function can be thought
        to be controller in MVC moudel. 

        ---------
        节点为主节点时的服务器，该函数有点像MVC模型里的控制器
        """
        data = await self.sever.reader.read()
        resp = {
            'get_main_node':        self.resp_main_node,
            'new_node':             self.resp_new_node,
            'new_main_node':        self.resp_new_main_node,
            'get_resource_file':    self.resp_resource_file,  #just response the resource file
            'main_node_fail':       self.resp_main_node_fail,    #just receive the info and do something
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
            'get_main_node':        self.get_main_node,
            'change_main_node':     self.change_main_node,
            'delete_node':          self.delete_node,
            'add_node':             self.add_node,
            'search_node':          self.search_node,
            'update_node':          self.update_node
        }
        pass
    

    async def notify(self, data, toips):
        """
        as a client connect to others' server to send info
        """
        if type(toips) is not type([]):
            toips = [toips]
        if type(data) is not type(''):
            data = json.dumps(data)
        for ip in toips:                        
            self.client.handler(ip)
            self.client.writer.write(data)
            await self.client.close_writer()

    async def requests(self,data, url=None):
        """
        as a client request to a server

        Return:
            json data
        """
        if not url:
            url = self.mainnode

        self.client.handler(url)
        if type(data) is not type(''):
            data = json.dumps(data)
        self.client.writer.write(data)
        await self.client.writer.drain()
        self.client.writer.write_eof()
        data = await self.client.reader.read()
        data = json.loads(data.decode()) 
        await self.client.writer.close()
        return data
    
    async def server(self, reader, writer):
        """
        as a server to handle request
        """

    async def send(self, data):         
        """
        as a server node to send info
        """
        addr = self.server.writer.get_extra_info('peername')
        if type(data) is not type(''):
            data = json.dumps(data)

        print(f"Received {data!r} from {addr!r}")
        print(f"Send: {data!r}")
        self.server.writer.write(data)
        await self.server.writer.drain()
        self.server.writer.write_eof()        
        print("Close the connection")
        self.server.writer.close()


    ########################################
    async def req_resource_file(self,url=None):
        data = {
            'op': 'get_resource_file'
        }
        return await self.requests(data, url)

    async def resp_main_node(self):
        res = {
            'scores': self.scores
        }
        await self.send(res)

    async def resp_new_node(self, data):
        await self.notify({
           'op': 'add_node',
            'node': data['node']
        }, self.scores)







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
            