import socket
import threading
import time
import random


def recv_data(udp_client_socket, mutex):
    client_port = random.randint(40000, 50000)
    local_addr = ('', client_port)  # 此处ip一般不用写，表示本机的任何一个ip
    udp_client_socket.bind(local_addr)  # 绑定ip和端口
    print('ready to receive……')
    while True:
        # 开启线程锁
        mutex.acquire()
        # 接收对方发送过来的数据，最大接收1024字节
        recv_data = udp_client_socket.recvfrom(1024)
        print('接收的数据为：', recv_data[0].decode('gbk'))
        # 解锁
        mutex.release()


def send_data(udp_client_socket, personal_id, server_ip_port):
    while True:
        # 提示用户输入数据
        send_user = input('输入目标用户ID号码：')
        send_content = input('请输入要发送的数据：')
        # 组包：当前用户 + 目标用户 + 数据
        send_pocket = personal_id + '\r\n' + send_user + '\r\n' + send_content
        # 准备socket
        dest_addr = server_ip_port  # 注意这里的服务器ip和端口！！！改！！！
        # 发送
        udp_client_socket.sendto(send_pocket.encode('gbk'), dest_addr)


def heart_jump(udp_client_socket, personal_id, server_ip_port):
    while True:
        # 设定一个指定的不存在的目标IP，便于服务器筛选
        send_pocket = personal_id + '\r\n' + '0.0.0.0' + '\r\n' + '0`0`0`0'
        # 准备socket
        dest_addr = server_ip_port  # 注意这里的服务器ip和端口！！！改！！！
        # 发送
        udp_client_socket.sendto(send_pocket.encode('gbk'), dest_addr)
        # 每分钟发送一次，向服务器表明该客户端的存活
        time.sleep(3)


# 实例化线程锁
mutex = threading.Lock()


def main():
    # tcp客户端构建流程
    # 1. 创建socket
    udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 2. 目的信息
    # server_ip = input('请输入服务器ip：')
    # server_port = int(input('请输入服务器端口号：'))
    server_ip_port = ('192.168.10.86', 8080)

    personal_id = input('请输入您的ID帐号：')
    # 启用子线程：接收服务器转发消息
    threading.Thread(target=recv_data, args=(udp_client_socket, mutex)).start()
    # 启用子线程：开始心跳，通知服务器已上线
    threading.Thread(target=heart_jump, args=(udp_client_socket, personal_id, server_ip_port)).start()
    # 启用子线程：向服务器发送消息
    threading.Thread(target=send_data, args=(udp_client_socket, personal_id, server_ip_port)).start()
    # tcp_client_socket.close()


if __name__ == '__main__':
    main()
