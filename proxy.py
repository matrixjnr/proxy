#!/usr/bin/python
host="127.0.0.1"
port=8888
byte=8192
listeners=5
agent="Safari"
 
 
###
# proxy.py
###
 
import socket, select, time, config, sys, re
from _thread import start_new_thread as thread
def Print(val):
    sys.stdin.flush()
    sys.stdout.write(val)
    
class ProxyServerData(object):
    def __init__(self, con, addr, data):
        self.bytes = config.byte
        self._con = con
        self._addr = addr
        self._data = data
        self.sock = socket.socket()
        self._sendAll()
 
    def _get_addr(self):
        data = self._data.split('\n')[0]
        try:
            url = data.split(" ")[1]
        except:
            m = re.search("CONNECT (.*?):443", data)
            print(m)
            url = m.group(0)
        h_pos = url.find("://")
        if (h_pos) ==-1:
            tmp = url
        else:
            tmp = url[(h_pos+3):]
            
        m = re.search("(.*\.\w+)", tmp)
        return m.group(0)
    
    def _get_port(self):
        url = self._get_addr()
        port_pos = url.find(":")
        if port_pos == -1:
            return 80
        else:
            m = re.search(":(\d+)", url)
            print(m.group(0))
    
    def _socket_format(self):
        return (self._get_addr(), int(self._get_port()))
 
    def _get_extra(self):
        data = self._data.split('\n')[0]
        url = data.split(" ")[1]
        h_pos = url.find("://")
        if h_pos == -1:
            extra = "/"
        else:
            url = url.replace("//", "")
            m = re.search("(/.+)", url)
        return m.group(0)
        
        
    def _sendAll(self):
        sock = self.sock
        try:
            sock.connect(self._socket_format())
            sock.send(data)
            while True:
                reply = sock.recv(self.bytes)
                if (len(reply) > 0):
                    self._con.send(reply)
                    dar = float(len(reply))
                    dar = float(dar / 1024)
                    dar = "%.3s" % (str(dar))
                    dar = "%sKB" % (dar)
                    print(("[*] Request Done: %s => %s <= %s" % (self._addr[0], dar)))
                else:
                    break
            sock.close()
            self._con.close()
        except:
            self._con.send("Error can't connect to %s" % self._get_addr())
            
class ProxyServer(object):
    def __init__(self):
        self._host = (config.host, config.port)
        self._socket = socket.socket()
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(False)
        self._agent = config.agent
        self._bytes = config.byte
        self._delay = config.delay
        self._listeners = config.listeners
        self._cons = list()
        self._log = Print
        self._proxy = ProxyServerData
 
    def _bind(self):
        self._socket.bind(self._host)
        self._socket.listen(self._listeners)
        
    def main(self):
        self._cons.append(self._socket)
        while True:
            rl, xl, wl = select.select(self._cons, [], [])
            for sock in rl:
                if sock == self._socket:
                    sock, ip = self._socket.accept()
                    self._on_connect()
                    self._cons.append(sock)
                elif sock == None:
                    self._socket.close()
 
                data = sock.recv(self._bytes)
                if not data:
                        self._on_close(sock)
                else:
                    agent = self._get_agent_header(data)
                    if not agent == "NO_AGENT":
                        agent_new = self._agent.replace("$MyAgent", agent)
                        data = data.replace(agent, agent_new)
                        thread(self._proxy, (sock, ip, data))
                    else:
                        thread(self._proxy, (sock, ip, data))
                
 
    def _on_close(self, sock):
        self._cons.remove(sock)
        self._log("client dc {0} left".format(self._count()))
        sock.close()
 
    def _on_connect(self):
        self._log("connection made, {0} clients connected".format(self._count()))
 
    def _count(self):
        c = len(self._cons) - 1
        return c
    
    def _get_agent_header(self, data):
        pat = "User-Agent: (.+)"
        m = re.search(pat, data)
        if m:
            return m.group(0)
        else:
            return "NO_AGENT"
        
    def _recvall(self, sock, count):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf  
if __name__ == '__main__':
    server = ProxyServer()
    server._bind()
    server.main()
