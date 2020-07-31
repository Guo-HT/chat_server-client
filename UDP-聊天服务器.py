import socket
import threading
import re
import time

Msg_Queue = []  # 消息队列
online_user = []  # 在线用户信息


# 正则处理接收数据
def recv_pocket_match(recv_data):
    # 通过正则表达式，将接受的数据包中的目的ip及实际数据分开，并重新组包
    ret = re.match(r'^(.*)\r\n(.*)\r\n(.*)', recv_data)
    # 分组，第一组为发送用户ID， 第二组为目标用户ID，第三组为数据内容
    return ret.group(1), ret.group(2), ret.group(3)


def recv_from_client(client_socket):
    local_addr = ('', 8080)  # 此处ip一般不用写，表示本机的任何一个ip
    client_socket.bind(local_addr)  # 绑定ip和端口
    print('>>> 等待客户端发送数据 <<<')
    while True:
        # 从客户端接收消息包
        data = client_socket.recvfrom(1024)
        # print(data.decode('gbk'))
        # 将数据包的数据部分正则提取
        recourse_id, dest_id, content = recv_pocket_match(data[0].decode('gbk'))
        # print(f'服务器接收到消息：{recourse_id}->{dest_id}->{content}')

        # 判断 发送数据的用户是否为在线状态
        for i in online_user:
            # 如果在线，则更新最新消息时间
            if i[0] == recourse_id:
                i[1] = time.time()
                break
        # 如果在用户中没有该用户，则将其添加入在线用户列表中
        else:
            online_user.append([recourse_id, time.time(), data[1]])
        # 判断用户发送的数据包为 心跳 or 实际数据，若是实际数据则添加进入消息队列
        if not (dest_id == '0.0.0.0' and content == '0`0`0`0'):
            print(f'用户{recourse_id}给用户{dest_id}发了如下消息：{content}')
            Msg_Queue.append((recourse_id, dest_id, content))


def send_to_client(client_socket):
    while True:  # 死循环遍历消息队列
        for recourse_id, dest_id, content in Msg_Queue:  # 从消息队列中读取任务
            for dest_user, old_time, addr in online_user:  # 验证目标用户是否在线
                if dest_user == dest_id:  # 若在线则发送消息
                    # 发送
                    # print(addr)
                    client_socket.sendto(content.encode('gbk'), addr)
                    # 消息发送后，将该任务从消息队列中移除
                    Msg_Queue.remove((recourse_id, dest_id, content))
        time.sleep(1)


def alive_judge():
    while True:  # 循环检测在线状态
        for recourse_id, old_time, data in online_user:  # 拆包，提取上一次通信时间
            time_minus = time.time() - old_time
            # print('time_minus', time_minus)
            # 若上一次通信在60秒前，则认为该用户已下线
            if time_minus > 3:
                # 将该用户从在线列表中移除
                online_user.remove([recourse_id, old_time, data])
        time.sleep(1)


def main():
    # 实例化socket，设定为UDP协议
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # while True:
    # 启用子线程：接收用户消息
    threading.Thread(target=recv_from_client, args=(socket_server,)).start()
    # 启用子线程：转发消息
    threading.Thread(target=send_to_client, args=(socket_server,)).start()
    # 启用子线程：检测用户存货
    threading.Thread(target=alive_judge).start()
    while True:
        # 每隔5秒输出一次在线用户和消息队列
        print(f'在线用户:{len(online_user)}人', online_user)
        print(f'消息队列:{len(Msg_Queue)}条', Msg_Queue)
        time.sleep(2)


if __name__ == '__main__':
    main()
