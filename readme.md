# 前期配置

## git 安装

* 简要的说 git 的作用： 

    我们在开发代码时，想象一个大一点的项目，每天就会都有一些更改。假如某一天改着改着突然发现出现了一个灾难性的问题。这时候一般就会想着和原先没有这个大问题时候的代码做一个对比，发现改动的地方，查找引发这个灾难的地方。

    git 就提供了这样的功能，git在每次提交（commit）代码的时候，都会自己隐藏的建立代码的版本信息，每次commit就是一个版本。然后就可以用git进行各种版本对比，版本回退等等工作。

    还有，就是在多人开发一个项目的时候，git也会帮助处理开放中的改动冲突，对代码进行合并等。举例说，A开发sk.py 文件， B开发sjgskjg.js 文件，他们提交到同一个地方的更改时，git就帮助合并他们的更改，保证项目都是最新的。

<a href="https://www.jianshu.com/p/414ccd423efc">git 安装教程</a>

<a href="https://www.cnblogs.com/tugenhua0707/p/4050072.html">git 使用教程</a>

安装完成后，就可以用git bash 里的 ssh 命令登录我们的远程服务器了
登录命令是 ssh root@78.141.190.51
之后输入密码就行。


# Union 的设计逻辑

## 定义
* union &nbsp;&nbsp;&nbsp;&nbsp;    项目名称，整个系统的名称. 一般的，一台电脑主机就是一个union节点，一个节点包含：连接器、区块链、服务器三类进程。
* 连接器 &nbsp;&nbsp; &nbsp;  union系统的一个进程，帮助在union系统的每台主机维护一份资源定位表
* 区块链 &nbsp; 区块链服务器为系统提供虚拟货币和智能合约功能。
* 服务器  &nbsp;&nbsp; &nbsp;    服务器也是一个进程，为客户端提供特定的服务。
* 资源定位表 &nbsp; 每台主机都会有的一份json文件，保存了union系统里的每个节点的连接信息
* 客户端 &nbsp;&nbsp; &nbsp; 客户端可以是浏览器、app；客户端首先连接任意节点更新资源定位表，之后连接 区块链 进行 钱包/身份 认证，之后在连接服务器获得服务。

Union系统是一整套的软件。通过它可以连接世界各地的电脑，并让这些电脑架设统一的服务器（软件），再由系统内的资源定位表提供给客户端自由的访问这些资源。我们每个人的个人电脑都是独立的，很多时候会有资源浪费，假如有一个软件，你只要运行它，就能出售自己电脑上多余的计算资源，获得相应的收入，那将会是很好的事。目前，有些国家会对一些常用的网站进行封锁，限制，造成互联网的不自由。思想有好的，也有坏的；检验的标准不是个人也不是民族的意志，而是用时间，淘优汰劣。Union就是以这两个目的为核心进行设计。

举例说：假设有网站A，还有游戏服务器B想架设在Union上；那么Union会分配系统内的一部分主机（个人电脑）安装A的软件，一部分主机安装B的软件；当客户端想访问网站A时，会先从Union获得资源定位表，也即资源定位表，然后挑选最合适的架设了A网站的主机访问A网站；所以A网站在设计时也要考虑到这种分布式的结构。资源定位表是Union内的每台主机都会有的，所以只要客户端连接上Union内的任意一台主机，就能获得网络内的所有资源。

以上是一个主体的思想，因为Union内的主机可以架设任意服务，所以当然也可以是VPN。整套网络需要一个安全机制，奖惩机制，身份验证机制，这都是通过区块链技术实现的。上一段说到的资源定位表，这也需要一个额外的服务对这个表进行更新维护，我们把这个服务称为连接器。这些就是Union系统最主要的三个部分：区块链部分， 可插拔的服务器， 连接器。 当然，还需要额外的客户端程序，这样才好访问整个网络。

## 区块链
区块链部分就是整套系统的奖惩以及账户管理系统。 会有用户钱包以及内置的虚拟币，暂定名字为unionCoin。 目前主要基于一个开源的区块链框架<a href="https://hyperledger-fabric.readthedocs.io/en/latest/whatis.html">Hyperledger Fabric</a>, 我开发了链码部分，用的是JavaScript语言。项目在<a href="https://github.com/f4f5/union">union </a>里。

## 连接器
连接器是一个独立的进程，它将帮助更新和维护资源定位表，并帮助调度客户端的连接。资源定位表包含Union中每个服务器的所有信息。因为整个网络是动态的，所以这个文件也会随时间变化。连接器将帮助进行资源定位表的增、删、改、查。资源定位表将按IP、服务器类型、端口、剩余连接、位置等描述服务器。资源定位表内容如下：

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

连接器将自动选择前100个SOCRE最高的计算机作为主节点。score越高意味着电脑在各种操作中都很快。经过一段时间后，普通节点将随机选择一个主节点来更新其资源定位表（如果需要）。

***删除失败的节点***

有两种状况，一个是失效节点是主节点，另一个是失效节点是普通节点。

*主节点故障*

* 如果失败的节点是主节点，当普通节点周期性地请求其父节点维持心跳时（该节点先前连接的主节点是父节点），如果请求被阻止，该节点将选择另一个主节点并将被阻止的主节点（原 父节点）报告给所选的主节点，然后所选的主节点将检查这个被阻塞的主节点状态，并更新资源定位表。为了实现这一点，普通节点会将曾连接的主节点作为其父节点来维护。

*普通节点故障*

* 主节点应该维护一个包含其所有子节点及其最新连接时间的表。如果心跳时间超出范围，父节点将尝试连接此节点并进行检查。如果失败，删除它，更新资源定位表。

***添加新节点***

* 如果一个新节点想要加入网络，它必须至少知道这个网络的一个节点的地址（IP，端口）。首先，它连接到该地址，并检索资源定位表。其次，根据当前资源定位表选择一个主节点，并连接到主节点。最后，在主节点接收到这些信息后，它将更新资源定位表。

***更新资源定位表***

* 只有主节点可以更新资源定位表。当一个主节点的资源定位表更新后，它将广播到所有主节点，所有主节点进行更新。当一个主节点接收到一个主节点的更新广播时，必须检查更新的节点是否有效，如果一个主节点在1小时内广播10次无效的节点，该节点将被放入一个主节点黑名单中一天。如果一个正常的节点在1小时内重新连接（不稳定）10次，它将在1小时内被此网络阻止。

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

## 服务器
当前的想法是弄一个VPN服务器，当然也可以弄个网站，一个内置的交易市场是需要的。GitHub的 f4f5 里已经上传的shadowsocks就是一个VPN服务器的源码。这个不是我写的，这个是网上开源的。

## Client API
## Server API
