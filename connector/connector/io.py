"""
dataio
"""
import asyncio

class Stream:
    def __init__(self, reader=None, writer=None):
        self.reader = reader
        self.writer = writer

    async def close_writer(self):
        await self.writer.drain()
        self.writer.write_eof()        
        self.writer.close()

class ServerStream(Stream):
    def __init__(self, reader=None, writer=None):
        pass

    async def handler(self, reader=None, writer=None):
        self.reader = reader
        self.writer = writer       


class ClientStream(Stream):
    def __init__(self, reader, writer):
        return super().__init__(reader, writer)

    async def handler(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8881)