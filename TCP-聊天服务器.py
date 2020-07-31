import threading
import socket
import time
import re

online_user = []
Msg_Queue = []


def recv_pocket_match(recv_data):
    '''通过正则表达式，将接受的数据包中的目的ip及实际数据分开，并重新组包'''
    ret = re.match(r'^(.*)\r\n(.*)\r\n(.*)', recv_data)
    # 分组，第一组为发送用户ID， 第二组为目标用户ID，第三组为数据内容
    return ret.group(1), ret.group(2), ret.group(3)


def recv_from_client(client_socket, client_addr):
    # 初始化变量 user_id，存储用户ID信息，并供该函数全局使用
    user_id = str()
    while True:
        try:
            # 循环接收该线程对应客户端发送的消息
            recv_data_row = client_socket.recv(1024)
            # 如果接收数据为空，decode报错，则捕获异常，断开连接
            recv_data = recv_data_row.decode('gbk')
            # 如果消息不为空
            try:
                # 判断是 -用户ID- 还是 -实际消息-
                # 如果是 -实际消息- ，则正则提取
                resourse_id, dest_id, content = recv_pocket_match(recv_data)
                # 将发送的信息以元组存入消息队列列表中
                print('接收到消息！')
                Msg_Queue.append((resourse_id, dest_id, content))
            except:
                # 若正则提取报错，则认为接收的信息为用户ID
                user_id = recv_data
                print(user_id, '已连接……')
                # 将该ID和当前tcp连接状态存入在线用户列表中
                online_user.append([user_id, client_socket, client_addr])
        except:
            # recv()解堵塞，但接收到的数据包为空：当前连接断开
            online_user.remove([user_id, client_socket, client_addr])
            client_socket.close()
            break


def send_to_client():
    while True:
        # 遍历在线用户列表
        for user_id, client_socket_online, client_addr in online_user:
            client_addr = client_addr
            # 遍历消息队列
            for resourse_id, dest_id, content in Msg_Queue:
                # 如果消息队列中的目的用户在线，则发送信息
                if user_id == dest_id:
                    send_pocket = resourse_id + '\r\n' + content
                    client_socket_online.send(send_pocket.encode('gbk'))
                    Msg_Queue.remove((resourse_id, dest_id, content))
                    break
        time.sleep(0.1)


def output_msg():
    '''每隔2秒输出一次在线用户和消息队列'''
    while True:
        print(f'在线用户:{len(online_user)}人', online_user)
        print(f'消息队列:{len(Msg_Queue)}条', Msg_Queue)
        time.sleep(2)


def main():
    # 实例化socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定IP、端口
    server_addr = ('', 8080)
    server_socket.bind(server_addr)
    # 开启监听
    server_socket.listen(128)
    # 输出在线用户和消息队列
    threading.Thread(target=output_msg).start()
    # 开启线程：向客户端发送消息
    threading.Thread(target=send_to_client).start()
    while True:
        # 分配服务socket
        client_socket, client_addr = server_socket.accept()
        print(f'连接到用户{client_addr}')
        # 开启线程：接收客户端消息
        threading.Thread(target=recv_from_client, args=(client_socket, client_addr)).start()


if __name__ == "__main__":
    main()
