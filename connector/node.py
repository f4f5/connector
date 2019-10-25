"""
node logic
author: kdsjkjgaksdgjqawe@outlook.com
"""
import sys
from ping import PyPing
import asyncio
import psutil
import util
from multiprocessing import Pool
import time
import speedtest
import random
import json
import local
from netio import ClientStream
import xmlrpc.client

__LINE__ = sys._getframe

class Node:
    def __init__(self):
        self.resource_mains = {}
        self.locations = {}
        self.server_types = {}
        self.remain_connections = {}
        self.scores = []   #ips 
        self.childs = []
        self.heart_beat = 1000
        self.last_beat = 0
        self.load_config()
        self.pingter = PyPing()
        self.ismainnode = False
        self.client = ClientStream(Node,Node)

    def load_config(self):
        serverConfig = {}
        with open('./config/server.json', encoding = 'utf8') as f:
            serverConfig = json.loads(f.read())
            self.server_type = serverConfig.get('server_type') 
            self.ip = serverConfig.get('ip')
            self.con_port = serverConfig.get('con_port')            
            self.api_port = serverConfig.get('api_port')     
            self.api_ip = self.ip + str(self.api_port)
            self.con_ip = self.ip + str(self.con_port)
            self.location = serverConfig.get('location')            
            self.remain_connection = serverConfig.get('remain_connection')
            self.score = serverConfig.get('score')
            self.pc = local.parse_pc_str(serverConfig.get('pc'))
            self.build_self_node()

    def build_self_node(self):
        self.node = {}
        self.node['con_ip'] = self.con_ip
        self.node['api_ip'] = self.api_ip
        self.node['remain_connection'] = self.remain_connection
        self.node['location'] = self.location
        self.node['score'] = self.score
        self.node['sever_type'] = self.server_type
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

        self.scores = js['scores']

        if len(self.scores) < 100 and len(self.scores)>=1:            
            rs = await self.req_resource_file(random.choice(self.scores))  
            self.node['father'] = self.con_ip          
            self.resource_mains = rs['resource_mains']
            self.locations = rs['locations']
            self.server_types = rs['server_types']
            self.remain_connections = rs['remain_connections']
            self.scores = rs['scores']
            self.ismainnode = True   # indicate the server will be main node server.
            util.opush(self.scores,self.con_ip)
            await self.notify({
                    'op': 'new_main_node',
                    'node': self.node
                }, self.scores)
            return
        elif len(self.scores) == 0:
            self.node['father'] = self.con_ip
            self.ismainnode = True   # indicate the server will be main node server.
            util.opush(self.scores,self.con_ip)          
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

    async def http_server(self, data, reader, writer):
        method = data.split(' ')[0]
        locate = data.split(' ')[1]
        if method == 'GET' and locate.startswith('/get_server'):
            ser_type = locate.split('/')[-1].strip('/')
            res = str(self.get_servers(ser_type))            
            writer.write(res.encode())            
        pass    

    async def main_node_server(self, data, reader, writer):
        """
        Server as a main node to receive and process data. This function can be thought
        to be controller in MVC moudel. 

        ---------
        节点为主节点时的服务器，该函数有点像MVC模型里的控制器
        """        
        
        resp = {
            'get_main_node':        self.resp_main_node,
            'new_node':             self.resp_new_node,
            'new_main_node':        self.resp_new_main_node,
            'get_resource_file':    self.resp_resource_file,  #just response the resource file
            'delete_main_node':     self.resp_delete_main_node,    
            'delete_node':          self.resp_delete_node,
            'add_node':             self.resp_add_node,
            # 'search_node':          self.search_node,
            # 'update_node':          self.update_node,
            'heart_beat':           self.resp_heart_beat,
            'set_main_node':        self.resp_set_main_node,
            'api':                  self.resp_api,
            'receive_connection':   self.api_receive_connection,
            'increase_connection':  self.resp_increase_connection
            
        }
        print('resp as  main server: ',data['op'])
        if data['op'] and resp.get(data['op']):
            await resp.get(data['op'])(data, reader, writer) 
        else:
            print(__LINE__().f_lineno,'resp fail as  main server: ',data['op'])       
        pass    
    
    async def node_server(self, data, reader, writer):
        """
        Server as a normal node to receive and process data. This function can be thought 
        to be controller in MVC moudel.

        ---------
        节点为常规节点时的服务器，该函数有点像MVC模型里的控制器
        """
        
        resp = {
            'get_main_node':        self.resp_main_node,
            'delete_node':          self.resp_delete_node,
            'get_resource_file':    self.resp_resource_file,  #just response the resource file
            'delete_main_node':     self.resp_delete_main_node,   
            'add_node':             self.resp_add_node,
            # 'search_node':          self.search_node,
            # 'update_node':          self.update_node,
            'heart_beat':           self.resp_heart_beat,
            'set_main_node':        self.resp_set_main_node,
            'api':                  self.resp_api,
            'receive_connection':   self.api_receive_connection,
            'increase_connection':  self.resp_increase_connection
        }
        print('resp as normal server: ',data['op'])
        if data['op'] and resp.get(data['op']):
            await resp.get(data['op'])(data, reader, writer) 
        else:
            print('resp fail as normal server: ',data['op'])       
        pass
    

    async def notify(self, data, toips):
        """
        as a client connect to others' server to send info
        """
        if type(toips) is not type([]):
            toips = [toips]
        if type(data) is not type(''):
            data = json.dumps(data)
        data = data.encode()
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

        await self.client.handler(url)
        if type(data) is not type(''):
            data = json.dumps(data)
        data = data.encode()
        self.client.writer.write(data)
        await self.client.writer.drain()
        self.client.writer.write_eof()
        print(__LINE__().f_lineno,'client send info succeed: ',data)
        data = await self.client.reader.read()
        data = json.loads(data.decode()) 
        self.client.writer.close()
        print(__LINE__().f_lineno,'client receive info succeed: ',data)
        return data
    
    async def server(self, reader, writer):
        """
        as a server to handle request
        """
        data = await reader.read()
        data = data.decode()
        tryhttp = False
        if data[0] == '{':
            try:
                data = json.loads(data)  
            except json.decoder.JSONDecodeError as es:
                tryhttp = True
                pass
        else:
            tryhttp=True                
        addr = writer.get_extra_info('peername')
        print(__LINE__().f_lineno,f"Received {data!r} from {addr!r}")
        print(f"Send: {data!r}")

        if tryhttp:
            await self.http_server(data, reader, writer)
        elif self.ismainnode:
            await self.main_node_server(data, reader, writer)
        else:
            await self.node_server(data, reader, writer)    

        await writer.drain()
        writer.write_eof()        
        print(__LINE__().f_lineno,"Close the connection")
        writer.close()

    async def send(self, data, reader, writer):         
        """
        as a server node to send info
        """
        addr = writer.get_extra_info('peername')
        if type(data) is not type(''):
            data = json.dumps(data)
        print(__LINE__().f_lineno,f"Send: {data!r}")        
        writer.write(data.encode())
        

    def set_node(self, data):
        if not self.server_types.get(data['server_type']):
            self.server_types[data['server_type']] = []
        util.opush(self.server_types[data['server_type']], data.ip)
        if not self.locations.get(data['location']):
            self.locations[data['location']] = []
        util.opush(self.locations[data['location']], data.ip)
        rem = ''
        re = int(data['remain_connection'])
        if re >= 0 and re < 100:
            rem = '10'
        elif re >= 100 and re < 1000:
            rem = '100'
        elif re >= 1000 and re < 10000:
            rem = '1000'
        elif re >= 10000 and re < 100000:
            rem = '10000'
        elif re > 100000:
            rem = 'unlimit'
        else:
            rem = 'unremain'
        if rem.startswith('1'):
            rem = 'remain' + rem                        
        util.opush(self.remain_connections[rem], data.ip)
        self.resource_mains[data.ip] = data
        pass

    def unset_node(self, data):
        ip = data['ip']
        self.server_types[data['server_type']].remove(ip)
        self.locations[data['location']].remove(ip)
        rem = ''
        re = int(data['remain_connection'])
        rem = self._get_connection_level(re) 
        self.remain_connections[rem].remove(ip)
        del self.resource_mains[ip]

    def get_servers(self, ser_type):
        return self.server_types.get(ser_type)


    def _get_connection_level(re):
        if re >= 1 and re < 100:
            rem = '10'
        elif re >= 100 and re < 1000:
            rem = '100'
        elif re >= 1000 and re < 10000:
            rem = '1000'
        elif re >= 10000 and re < 100000:
            rem = '10000'
        elif re > 100000:
            rem = 'unlimit'
        else:
            rem = 'unremain'
        if rem.startswith('1'):
            rem = 'remain' + rem  
        return rem

    def increase_connection(self, ip=Node):
        if not ip:
            ip = self.con_ip
        if self.resource_mains.get(ip):
            self.resource_mains[ip]['remain_connection'] -=1
        else:
            return False
        rem = ''
        re = int(self.resource_mains[ip]['remain_connection'])
        rem = self._get_connection_level(re)
        pre_rem = self._get_connection_level(re+1)
        if rem == pre_rem:
            return True
        else:
            self.remain_connections[pre_rem].remove(ip)
            util.opush(self.remain_connections[rem], ip)
            return True

    def decrease_connection(self, ip=Node):
        if not ip:
            ip = self.con_ip
        if self.resource_mains.get(ip):
            self.resource_mains[ip]['remain_connection'] +=1
        else:
            return False
        rem = ''
        re = int(self.resource_mains[ip]['remain_connection'])
        rem = self._get_connection_level(re-1)        
        self.remain_connections[rem].remove(ip)
        return True

    def update_connection(self, ip, conn):
        rem = ''
        re = int(self.resource_mains[ip]['remain_connection'])
        rem = self._get_connection_level(conn)
        pre_rem = self._get_connection_level(re)
        self.resource_mains[ip]['remain_connection'] = conn
        if rem != pre_rem:            
            self.remain_connections[pre_rem].remove(ip)
            util.opush(self.remain_connections[rem], ip)

    ########################################
    async def req_resource_file(self,url=None):
        data = {
            'op': 'get_resource_file'
        }
        return await self.requests(data, url)



    #########################################

    async def resp_resource_file(self, data, reader, writer):
        await self.send({
            'resource_mains': self.resource_mains,
            'locations': self.locations,
            'server_types': self.server_types,
            'remain_connections': self.remain_connections,
            'scores': self.scores
        },reader, writer)

    async def resp_main_node(self, data, reader, writer):
        print(__LINE__().f_lineno, 'resp get_main_node')
        res = {
            'scores': self.scores
        }
        await self.send(res, reader, writer)

    async def resp_new_node(self, data, reader, writer):
        self.set_node(data)
        util.opush(self.childs, data.ip)
        await self.notify({
           'op': 'add_node',
            'node': data
        }, self.scores)
    
    async def resp_new_main_node(self, data, reader, writer):
        await self.notify({
           'op': 'add_node',
            'node': data
        }, self.scores)

    async def resp_add_node(self, data, reader, writer):
        if not self.server_types.get(data['server_type']):
            self.server_types[data['server_type']] = []
        util.opush(self.server_types[data['server_type']], data.ip)
        if not self.locations.get(data['location']):
            self.locations[data['location']] = []
        util.opush(self.locations[data['location']], data.ip)
        rem = ''
        re = int(data['remain_connection'])
        if re >= 0 and re < 100:
            rem = '10'
        elif re >= 100 and re < 1000:
            rem = '100'
        elif re >= 1000 and re < 10000:
            rem = '1000'
        elif re >= 10000 and re < 100000:
            rem = '10000'
        elif re > 100000:
            rem = 'unlimit'
        else:
            rem = 'unremain'
        if rem.startswith('1'):
            rem = 'remain' + rem                        
        util.opush(self.remain_connections[rem], data.ip)
        self.resource_mains[data.ip] = data
        if self.ismainnode:
            await self.notify({
                'op': 'add_node',
                    'node': data
                }, self.childs)

    async def resp_set_main_node(self, data, reader, writer):
        util.opush(self.scores, data['ip'])
        if self.con_ip == data['ip']:
            self.ismainnode = True
            self.childs = []
        if self.ismainnode and self.con_ip != data['ip']:
            await self.notify({'op':'set_main_node', 'ip': data['ip']},self.childs)


    async def resp_heart_beat(self, data, reader, writer):
        await self.send('1', reader, writer)

    async def resp_delete_main_node(self, data, reader, writer):        
        self.scores.remove(data['node']['ip'])
        self.unset_node(data)
        if self.con_ip == self.scores[0]:
            keys = list(self.resource_mains.keys())
            random.shuffle(keys)
            if len(keys) >5000:
                keys = keys[:5000]
            scores = sorted(keys, key= lambda x:self.resource_mains[x]['score'])
            mainnode = ''
            for k in scores:
                if self.scores.count(k) == 0:
                    mainnode = k
                    break
            self.scores.push(mainnode)
            await self.notify({'op': 'set_main_node', 'ip': mainnode}, self.scores)

            # reselect the 100s
        if self.ismainnode:
            await self.notify({'op': ' delete_node', 'node': data}, self.childs)

    async def resp_delete_node(self, data, reader, writer):
        self.unset_node(data)

    async def resp_api(self, data, reader, writer):
        """
        response client request for api 
        Args:
        --
        data:  { op: , server_type : , geolocation:}

        Return:
        --
        the best server ip.
        """
        candidate = ''
        candidate0 = self.server_types.get(data.get('server_type'))
        candidate1 = self.server_types.get(data.get('geolocation'))
        if candidate0 and candidate1:
            l = list(set(candidate0).intersection(set(candidate1)))
            if len(l) <=0:
                candidate = candidate0
            else:
                candidate = l
        if candidate and len(candidate)<=0:
            return await self.send({}, reader, writer)

        if len(candidate) ==1:
            return await self.send(self.resource_mains[candidate[0]], reader, writer)
        random.shuffle(candidate)
        best = candidate[0]
        count = 0
        for ser in candidate:
            if(self.resource_mains[best].remain_connection < self.resource_mains[ser].remain_connection):
                best = ser
                count =+1
                if count > 20:
                    break

        await self.send(self.resource_mains[best], reader, writer)



    async def api_receive_connection(self, data, reader, writer):
        """
        this computer gonna receive connection from clients
        this function help to validate the connection and update current node
        args:
        ---
        data: {'reference': , server_type : , geolocation: }
        """                   
        checked = await self.requests({'op': 'validate_connection', 'server_type' : data['server_type'], 'geolocation': data['geolocation']}, data['reference'])     
        if checked:
            self.increase_connection()
            await self.notify({'op':'increase_connection','con_ip': self.con_ip}, self.scores)

    async def resp_increase_connection(self,data, reader, writer):
        self.increase_connection(data['con_ip'])
        if self.ismainnode:
            await self.notify({'op':'increase_connection','con_ip': data['con_ip']}, self.childs)
    
    async def periodic_do(self):
        self.last_beat = int(time.time())
        if self.ismainnode:
            await self.check_main_heartbeat()
        else:
            await self.check_child_heartbeat()
        
        conn = self.check_api_connection()
        self.update_connection(self.con_ip, conn)
        pass 

    async def check_child_heartbeat(self):
        for child in self.childs:
            data = await self.requests({'op': 'check_hearbet'}, child)
            if str(data) is not '1':
                await asyncio.sleep(10)
                data = await self.requests({'op': 'check_hearbet'}, child)
                if str(data) is not '1':
                    await self.notify({'op': 'delete_node', 'node': child}, self.scores)

    async def check_main_heartbeat(self):
        data = await self.requests({'op': 'check_hearbet'}, self.mainnode)
        if str(data) is not '1':
            await asyncio.sleep(12)
            data = await self.requests({'op': 'check_hearbet'}, self.mainnode)
            if str(data) is not '1':
                self.scores.remove(self.mainnode)
                await self.notify({'op': 'delete_main_node', 'node': self.mainnode}, self.scores)
                if self.last_beat and int(time.time()) - last_beat > self.heart_beat*2:
                    self.connect_2_network(random.choice(self.scores))
                else:
                    self.scores = await self.requests({'op':'get_main_node'}, url)
                    mainnode =self.choose_best_mainnode()
                    self.node['father'] = mainnode
                    self.mainnode = mainnode  
                      
    def check_api_connection(self):
        """
        * only connect to local server.

        this function help to check whether local server is available, and fetch
        the remain connection.
        """
        # with xmlrpc.client.ServerProxy("http://localhost:8000/") as proxy:
        #     print("3 is even: %s" % str(proxy.is_even(3)))
        #     print("100 is even: %s" % str(proxy.is_even(100)))
        return 9
        pass