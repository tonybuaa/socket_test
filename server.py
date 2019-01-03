import socket
import select
import queue

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(('0.0.0.0', 10001))
server.listen(10)
print('server:', server)

rlist = [server]
wlist = []
message_queues = {}

while rlist:
    print('while rlist:', list(map(lambda x: (x.fileno(), x.getsockname()), rlist)))
    rds, wds, eds = select.select(rlist, wlist, [], 20)
    print(list(map(lambda x: x.fileno(), rds)),
          list(map(lambda x: x.fileno(), wds)),
          list(map(lambda x: x.fileno(), eds)))
    for r in rds:
        print('\tr', r.fileno())
        if r is server:
            conn, c_addr = r.accept()
            print('\t\tafter accept:', list(map(lambda x: x.fileno(), rds)),
                  list(map(lambda x: x.fileno(), wds)),
                  list(map(lambda x: x.fileno(), eds)))
            print('\t\tconn:', (conn.fileno(), conn.getsockname(), conn.getpeername()), 'c_addr:', c_addr)
            conn.setblocking(False)
            rlist.append(conn)
            message_queues[conn] = queue.Queue()
        else:
            data = r.recv(1024)
            if data:
                print('\t\tdata:', data, 'from:', r.getpeername())
                message_queues[r].put(data)
                if r not in wlist:
                    wlist.append(r)
            else:
                print('\t\tclosing', c_addr)
                if r in wlist:
                    wlist.remove(r)
                rlist.remove(r)
                r.close()
                del message_queues[r]

    for w in wds:
        print('\tw', w.fileno())
        try:
            next_msg = message_queues[w].get_nowait()
        except queue.Empty:
            print('\t\t', w.getpeername(), 'queue empty')
            wlist.remove(w)
        else:
            print("\t\tsending ", next_msg, " to ", w.getpeername())
            w.send(next_msg)
