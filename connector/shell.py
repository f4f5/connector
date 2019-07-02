"""
command line relate operation
"""

import sys
import asyncio
from node import Node

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
else:
    loop = asyncio.get_event_loop()
    
asyncio.set_event_loop(loop)

ip = ''
port = 0
with open('./config/server.json', encoding = 'utf8') as f:
    serverConfig = json.loads(f.read())
    ip = serverConfig.get('ip')
    port = serverConfig.get('port')

async def main():
    node = Node()
    server = await asyncio.start_server(
        node.server, ip, port)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()
asyncio.run(main())