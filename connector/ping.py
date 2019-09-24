
import sqlite3
import struct
import socket
# import socks
import time

class PyPing(object):
    def wrap_ping(self, ip):
        self.ping(0,ip)
    def ping(self, i, ip):
        try:
            raw_socket = socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
            # 首先对要发送的字段进行打包
            packet = struct.pack('!BBHHH32s', 8, 0, 0, i,
                                 0, b'abcdefghijklmnopqrstuvwabcdefghi')
            # 计算ICMP校验和
            checksum = self.do_checksum(packet)
            # 将校验和得到的数字打包入发送的内容
            packet = struct.pack('!BBHHH32s', 8, 0, checksum,
                                 i, 0, b'abcdefghijklmnopqrstuvwabcdefghi')
            # 发送数据
            raw_socket.sendto(packet, (ip, 0))
            s_time = time.time() *1000
            # 接收数据
            recv_data = raw_socket.recvfrom(1024)
            # 解包数据
            data = struct.unpack('!BBHHH32s', recv_data[0][20:])[-1]
            # 判断数据内容
            if data == b'abcdefghijklmnopqrstuvwabcdefghi':
                e_time = time.time() * 1000
                print(e_time - s_time)
            else:
                print('内容错误')
        except Exception as e:
            print(e, '连接超时')

        # 对ICMP进行校验和
    def do_checksum(self, string):
        checksum = 0
        # 将内容等分求和，每两个字节为16bit
        for i in range(0, len(string), 2):
            # checksum 和 (string[i] << 8 + string[i+1]) 这个16bit二进制的数求和。
            checksum += string[i] << 8
            checksum += string[i+1]
            # 倘若 checksum 大于 0xffff ，则表明 checksum 现在为17 bit
            if checksum > 0xffff:
                # checksum 减去 (0xffff + 1) + 1 ，是将进位看成 1 ，并相加
                checksum -= 0xffff
        # 去反
        checksum = ~checksum
        # 求正
        checksum &= 0xffff
        return checksum

    def more_ping(self, n, ip, timeout, proxies):
        self.set_timeout(timeout)
        self.set_proxy(proxies['address'], proxies['port'])
        for i in range(n):
            self.ping(i, ip)

    @staticmethod
    # 设置 timeout
    def set_timeout(timeout):
        socket.setdefaulttimeout(timeout)

    # @staticmethod
    # # 设置代理
    # def set_proxy(address, port):
    #     socks.set_default_proxy(socks.HTTP, address, port)

if __name__ == "__main__":
    PyPing.wrap_ping('www.baidu.com')