"""
使用多路复用器select实现的简单的多进程高性能reactor
"""
import socket
import select
import time
from multiprocessing import Process, Queue, cpu_count


def single_process(socket_queue, process_id):
    r_fd = set()
    w_fd = set()
    e_fd = set()
    while True:
        if socket_queue.qsize() > 0:
            c = socket_queue.get()
            r_fd.add(c)
            w_fd.add(c)
            e_fd.add(c)
        if r_fd or w_fd or e_fd:
            r_socket, w_socket, e_socket = select.select(r_fd, w_fd, e_fd)
            # 只关注可读事件
            del_list = []
            for s in r_socket:
                try:
                    msg = s.recv(1024)
                    print(process_id, s.fileno(), msg)
                    if msg:
                        s.send(msg)
                    else:
                        del_list.append(s)
                        s.close()
                except:
                    pass
            for s in del_list:
                r_fd.remove(s)
                w_fd.remove(s)
                e_fd.remove(s)
        time.sleep(1 / 1000)


if __name__ == '__main__':
    server = socket.socket()
    host = '127.0.0.1'
    port = 5005
    server.bind((host, port))
    server.listen(1000)
    server.setblocking(False)

    cpu_nums = cpu_count()
    sockets_list = []
    for n in range(cpu_nums):
        sockets_list.append(Queue(1000))

    all_process = []
    for n in range(cpu_nums):
        p = Process(target=single_process, args=(sockets_list[n], n))
        all_process.append(p)

    for p in all_process:
        p.start()

    index = 0
    while True:
        try:
            client, addr = server.accept()
            client.setblocking(True)
            if index == cpu_nums:
                index = 0
            sockets_list[index].put(client)
            index += 1
        except:
            pass
        time.sleep(1 / 1000)




