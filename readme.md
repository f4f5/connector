# Union 的设计逻辑
Union系统通过网络连接世界各地的电脑，并让这些电脑架设统一的服务器（软件），再由系统内的资源路由表提供给客户端自由的访问这些资源。举例说：假设有网站A，还有游戏服务器B想架设在Union上；那么Union会分配系统内的一部分主机（个人电脑）安装A的软件，一部分主机安装B的软件；当客户端想访问网站A时，会先从Union获得资源路由表，也即资源定位表，然后挑选最合适的架设了A网站的主机访问A网站；所以A网站在设计时也要考虑到这种分布式的结构。资源定位表是Union内的每台主机都会有的，所以只要客户端连接上Union内的任意一台主机，就能获得网络内的所有资源。

以上是一个主体的思想，因为Union内的主机可以假设任意服务，所以当然也可以是VPN。整套网络需要一个安全机制，奖惩机制，身份验证机制，这都是通过区块链技术实现的。上一段说到的资源定位表，这也需要一个额外的服务对这个表进行更新维护，我们把这个服务称为连接器。这些就是Union系统最主要的三个部分：区块链部分， 可插拔的服务器， 连接器。 当然，还需要额外的客户端程序，这样才好访问整个网络。

## 区块链
## 区块链服务器
## 连接器
连接器将帮助更新和维护资源路由表，并帮助调度客户端的连接。资源路由表包含Union中每个服务器的所有信息。因为整个网络是动态的，所以这个文件也会随时间变化。连接器将帮助进行这些更改。资源路由表将按IP、服务器类型、端口、剩余连接、位置等描述服务器。资源路由表内容如下：

```
resource_main:    //主资源文件
{
    ip_x: {
        server_type: []
        ports:[]
        remainconnections: []
        score:
        location:
    }    
}
locations:   //下面的数据结构帮助更快的搜索资源
{
    location_x: {  //是该按国家进行划分吗？ 待定
        ip:
    }
}

scores: [1st ip, 2ed ip, 3rd ip, 4th ip, ...]  //前100个性能最好的主机

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

连接器将自动选择前100个SOCRE最高的计算机作为主节点。score越高意味着电脑在各种操作中都很快。经过一段时间后，普通节点将随机选择一个主节点来更新其资源路由表（如果需要）。

***删除失败的节点***

有两种状况，一个是失效节点是主节点，另一个是失效节点是普通节点。

*主节点故障*

* 如果失败的节点是主节点，当普通节点周期性地请求其父节点维持心跳时（该节点先前连接的主节点是父节点），如果请求被阻止，该节点将选择另一个主节点并将被阻止的主节点（原 父节点）报告给所选的主节点，然后所选的主节点将检查这个被阻塞的主节点状态，并更新资源路由表。为了实现这一点，普通节点会将曾连接的主节点作为其父节点来维护。

*普通节点故障*

* 主节点应该维护一个包含其所有子节点及其最新连接时间的表。如果心跳时间超出范围，父节点将尝试连接此节点并进行检查。如果失败，删除它，更新资源路由表。

***添加新节点***

* 如果一个新节点想要加入网络，它必须至少知道这个网络的一个节点的地址（IP，端口）。首先，它连接到该地址，并检索资源路由表。其次，根据当前资源路由表选择一个主节点，并连接到主节点。最后，在主节点接收到这些信息后，它将更新资源路由表。

***更新资源路由表***

* 只有主节点可以更新资源路由表。当一个主节点的资源路由表更新后，它将广播到所有主节点，所有主节点进行更新。当一个主节点接收到一个主节点的更新广播时，必须检查更新的节点是否有效，如果一个主节点在1小时内广播10次无效的节点，该节点将被放入一个主节点黑名单中一天。如果一个正常的节点在1小时内重新连接（不稳定）10次，它将在1小时内被此网络阻止。

***路由逻辑***

* 假设一个主节点连接失败，它将被从主节点列表中删除。然后选择一个新节点添加到主节点列表中。首先，新的主节点将没有子节点，因此没有父节点的普通节点将首先选择子节点少的主节点连接。当所有主节点的子节点数量达到一个大致的平衡是，我们就要考虑到主节点与子节点的距离问题。因为子节点与主节点之间的通信是很频繁的，所有选择较近的节点做为主节点是很有必要的。

* 主节点将有自己的容量。所有接收连接的主节点都应该保持某种平衡。应该有一个函数来计算主节点连接的中值点。连接首先遵循就近原则，然后再挑选链接数少的。假设我们有一个函数可以计算正常节点连接到的所有主节点的效率。或者说是，延误率或损失率或它们两者的综合的一个评分，这个评分越低越好或越大越好。这时普通节点应该总是选择最好的主节点连接。算法将是：

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
