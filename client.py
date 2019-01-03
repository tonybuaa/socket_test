import socket

socks = []
messages = ["This is the message",
            "It will be sent",
            "in parts "]

for i in range(5):
    socks.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

for s in socks:
    s.connect(("127.0.0.1", 10001))

counter = 0
for m in messages:
    for idx, s in enumerate(socks):
        s.send("{} v: {}".format(m, idx).encode())
    for idx, s in enumerate(socks):
        data = s.recv(1024)
        print("received {}".format(data))
        if not data:
            print("closing socket ", s.getpeername())
            s.close()
