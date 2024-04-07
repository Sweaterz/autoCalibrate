import socket


HOST = '192.168.1.200'

PORT = 2111 # TCP port
# PORT = 5001 # UDP port

ADDR = (HOST, PORT)
BUFFSIZE = 2048
MAX_LISTEN = 5


def tcpServer():
    pass


def tcpClient():

    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        # 尝试连接客户套接字
        s.connect(ADDR)
        print('连接成功')
        num = 0
        data = []
        pointsData = []
        while num < 50:
            recv_data = s.recv(BUFFSIZE)
            # print('返回数据信息：{!r}'.format(recv_data))

            if f"{recv_data[0]:X}" == "FC" and f"{recv_data[1]:X}" == "FD" and f"{recv_data[2]:X}" == "FE" and f"{recv_data[3]:X}" == "FF":
                data.extend(recv_data)
            else:
                if 0 < len(data) < 1813:
                    data.extend(recv_data)
                else:
                    continue
            if len(data) == 1813:
                oneData = data
                data = []
                # print(oneData)
                num += 1
                # 报文长度， 报文标志， 设备序列号， 报文内容, 校验和
                msgLength, msgFlag, content, checksum = parseData(oneData)
                points = parseContent(content)
                pointsData.append(points)
    return pointsData


def parseData(oneData):
    msgLength = oneData[4] + oneData[5] * 256
    msgFlag = oneData[6: 8]
    content = oneData[8: -2]
    checksum = oneData[-2:]
    return msgLength, msgFlag, content, checksum


def parseContent(content):
    points = []
    deviceNum = "{:02X}{:02X}{:02X}{:02X}".format(content[3], content[2], content[1], content[0])
    frequency = (content[8] + content[9] * 256) * 0.01 # 50
    pointNum = content[10] + content[11] * 256 # 881
    startAngle = (content[12] + content[13] * 256 + content[14] * 256 * 256 + content[15] * 256 * 256 * 256) * 0.0001 # 35
    angleStep = content[16: 18] # 0.125
    versionFlag = content[18] # V1.0
    flag = content[19] # 0
    #   --关闭滤波
    alarmWindowPollution = content[20] # 0 窗口污染预警
    inputSignal = content[21]
    reserve = content[22: 40]
    verticalAngle = content[40: 41]
    pointsData = content[41:]
    print(deviceNum)
    for i in range(pointNum):
        distance = pointsData[2 * i] + pointsData[2 * i + 1] * 256
        points.append(distance)

    return points


def udpClient():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            recvData, addrs = s.recvfrom(BUFFSIZE)
            print('recv message : {}'.format(recvData.decode('utf-8')))


if __name__ == '__main__':
    num = 0
    tcpClient()