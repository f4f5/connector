# Desine Logic Of Union
## Block Chain
## Blockchain Client Server
## Connector
connector will help to update and maintain the resource file, and also help to dispatch client connections.

The resource file contains all the infomation about every server's information in Union. Coz the whole network is dynamic so this file will also change among time. Connector will help to make these changes. A resource file will descript a server by ip, server type, ports, remain connections, location, etc. Resource file content looks like this:
```
resource_main:    //the main resource file
{
    ip_x: {
        server_type: []
        ports:[]
        remainconnections: []
        score:
        location:
    }    
}
locations:   //below structure help to search faster
{
    location_x: {  country? the same country first paired
        ip:
    }
}

scores: [1st ip, 2ed ip, 3rd ip, 4th ip, ...]  //the firt 100 ips

server_type:
{
    type_x: [ip_x]
}

remainconnections:{
    unremain: [],
    remain10: [],
    remain100: [],
    remain1000: []
    unlimit: []
}

```
The connector system will automaticly select the first 100 high socre computor as the main node. A high sore means the computer fast in all kind of opration. After a period of time, common node will randomly select a main node to update their resource file if neccesary.

 ***Delete Failed Node***

There are two conditions, one is that the failed node is the main node, another one is that the failed node is a normal node. 

*main node fail*
* If the failed node is a main node, when the normal node periodically request for its father node for heartbeat, the father node which is the main node the node previously connect to, if the request is blocked, the node will select another main node and report the blocked main node to the selected one, and then the selected on will check the blocked main node's condition, and to update the resource file. To achieve this, a normal node should maintain the previous connected mainnode as its father node.

*normal node fail*
* The main node should maintain a table that contains all its child nodes and its their latest connected time. If the heartbeat time is out of range, the father node will try to connect this node and check it. if failed, delete it, update resource file.

***Add New Node***
* If a new node want to join the network, it have to know at least one address(ip, port) of this network. Firstly, it connects to the address, and retrieves resource file. Secondly, it choose a mainnode base on the current resource file, and connect to the mainnode. Thirdly, after the mainnode recieve this information, it will update the resource file.

***Update Resource File***
* Only mainnode can update the resource file. When one of the mainnode's resource file updated, it will broadcast to all main node, and the all the mainnode do the update. When a mainnode receive a mainnode's update broadcast, it must check the update valid, if a main node broadcast an unvalid node for ten times within 1 hour, the node will be put into a mainnode blacklist for one day. If a normal node reconnect (unstable) 10 times within 1 hour, it will be blocked from this network for 1 hour.

***Route Logic***
* Suppose a main node fail to connect with, it will be deleted out of the mainnode list. And then a new node will be selected to be added to the main node list. At first, the new main node will have no children, so the no-father-node will firstly choose the children less node to connect to. But there will be more complicaty cause we have to make the distance into consideration.

* The main node will have there own capacity. And all main nodes receive connects should be keep in some kind of balance. There should be a function that calculate the median poiont of connections. The connection firstly base on the nearest first, and then the less first.  Suppose we have a function that could calculate the all main node's efficiency when a normal node connect to. Or another phrase, the delay or loss rate or a comprehensive number, which is the lower the better or the larger the better. then the node should always choose the best on at this moment. The algorithm will be:
```
    choose_best_main_node(current_node):
        efficients = []
        for node in main_node_list:
            efficents.push(comprehensive_efficient(current_node, node) )
        index = maxIndexOf(efficients)
        return efficients[index]    
```

### Design
Add  Delete  Update  Search
Choose the best 100 point to be main point

Flows 0: 
initialization, for the config file and the pc efficient data.


Flows 1:  Function  connect_2_network
check for self node to fill some infomation  ...on going
connect to the network to retrive mainnode   ... on going
connect to mainnode to get more info
prepare for mainnode if possible

Flows2:
a node periodically upload itself to its mainnode
if  mainnode block, change its mainnode and tell the new mainnode this block

Flows3:
a mainnode check for its child's heartbeat periodically. if block delete.

Flows4:
mainnode exchange infomation if need

Flows5: 
delete An old Mainnode and select a new one.

## Client API
## Server API
