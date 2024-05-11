"""
Algorithm for calibration
用于自动标定的算法
"""


import math
import numpy as np
from receiveLaserData import tcpClient
from plotPoints import point

lidarAngleStep = 0.125
lidarStartAngle = 0


# data = [[distance1, distance2, distance3, ...], [distance1, distance2, distance3, ...],...]
def calibration(data):
    iHorizontalAngle = get_iHorizontalAngle(data)
    iHorizontalHeight = get_iHorizontalHeight(data, iHorizontalAngle)
    minDistance = get_minDistance(data, iHorizontalAngle, iHorizontalHeight)
    maxDistance = get_maxDistance(data, iHorizontalAngle, iHorizontalHeight, minDistance)
    return iHorizontalAngle, iHorizontalHeight, minDistance, maxDistance


def get_iHorizontalAngle(data):
    # 参与标定的帧数
    dataSize = len(data)
    thetaList = []
    # 获取对应距离的数据
    for idx, data_per_id in enumerate(data):
        usedData = []
        tanList = []
        for i, distance in enumerate(data_per_id):
            if 2060 <= distance <= 3640:
                angle = i * lidarAngleStep + lidarStartAngle
                h = int(math.sin(math.radians(angle)) * distance)
                l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                usedData.append([l, h])
            else:
                continue
        countNum = len(usedData) // 2
        for i in range(countNum):
            l1 = usedData[i][0]
            l2 = usedData[i + countNum][0]
            h1 = usedData[i][1]
            h2 = usedData[i + countNum][1]
            if l1 != l2:
                theta = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
                tanList.append(theta)
        # for i in range(len(usedData) - 10):
        #     l1 = usedData[i][0]
        #     l2 = usedData[i + 10][0]
        #     h1 = usedData[i][1]
        #     h2 = usedData[i + 10][1]
        #     if l1 != l2:
        #         theta = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
        #         tanList.append(theta)
        if len(tanList) != 0:
            average = sum(tanList) / len(tanList)
        else:
            return 60
        # 最大值和最小值之差应该满足小于0.5度
        while max(tanList) - min(tanList) > 0.5:
            diff = [math.fabs(tan - average) for tan in tanList]
            m = max(diff)
            index = diff.index(m)
            value = tanList[index]
            tanList.remove(value)
            average = sum(tanList) / len(tanList)
        thetaList.append(average)
    average = sum(thetaList) / len(thetaList)
    while max(thetaList) - min(thetaList) > 0.5:
        diff = [math.fabs(theta - average) for theta in thetaList]
        m = max(diff)
        index = diff.index(m)
        value = thetaList[index]
        thetaList.remove(value)
        average = sum(thetaList) / len(thetaList)
    iHorizontalAngle = sum(thetaList) / len(thetaList)
    return iHorizontalAngle


def get_iHorizontalHeight(data, iHorizontalAngle):
    dataSize = len(data)
    heightList = []
    for idx, data_per_idx in enumerate(data):
        usedData = []
        for i, distance in enumerate(data_per_idx):
            # 保证1.2m-3.5m是路面
            if 2060 <= distance <= 3640:
                angle0 = i * lidarAngleStep + lidarStartAngle
                if angle0 < iHorizontalAngle:
                    angle = iHorizontalAngle - angle0
                    h = - int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > iHorizontalAngle:
                    angle = angle0 - iHorizontalAngle
                    h = + int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = 0
                    l = distance
                usedData.append(h)
            else:
                continue
        if len(usedData) == 0:
            return 1500
        average = sum(usedData) / len(usedData)
        while max(usedData) - min(usedData) > 0.5:
            diff = [math.fabs(data - average) for data in usedData]
            m = max(diff)
            index = diff.index(m)
            value = usedData[index]
            usedData.remove(value)
            average = sum(usedData) / len(usedData)
        heightList.append(sum(usedData) / len(usedData))
    average = sum(heightList) / len(heightList)
    while max(heightList) - min(heightList) > 0.5:
        diff = [math.fabs(height - average) for height in heightList]
        m = max(diff)
        index = diff.index(m)
        value = heightList[index]
        heightList.remove(value)
        average = sum(heightList) / len(heightList)
    iHorizontalHeight = - max(heightList) - 20
    return iHorizontalHeight


def get_minDistance(data, iHorizontalAngle, iHorizontalHeight):
    # 参与标定的帧数
    dataSize = len(data)
    minDistanceList = []
    # 获取对应距离的数据
    for idx, data_per_idx in enumerate(data):
        usedData = []
        for i, distance in enumerate(data_per_idx):
            # 保证1.2m-3.5m是路面
            if 0 <= distance <= 2000:
                angle0 = i * lidarAngleStep + lidarStartAngle
                if angle0 < iHorizontalAngle:
                    angle = iHorizontalAngle - angle0
                    h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                elif angle0 > iHorizontalAngle:
                    angle = angle0 - iHorizontalAngle
                    h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance)
                    l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                else:
                    h = iHorizontalHeight
                    l = distance
                usedData.append([l, h])
            else:
                continue
        for l, h in usedData:
            if 300 < l < 2500 and h < 0:
                minDistanceList.append(l)
                break
    if len(minDistanceList) == 0:
        return 900
    average = sum(minDistanceList) / len(minDistanceList)
    while max(minDistanceList) - min(minDistanceList) > 50:
        diff = [math.fabs(distance - average) for distance in minDistanceList]
        m = max(diff)
        index = diff.index(m)
        value = minDistanceList[index]
        minDistanceList.remove(value)
        average = sum(minDistanceList) / len(minDistanceList)
    return average


def get_maxDistance(data, iHorizontalAngle, iHorizontalHeight, minDistance):
    return minDistance + 3000


if __name__ == '__main__':
    data = tcpClient()

    angle, height, minl, maxl = calibration(data)
    # 默认角度：60    默认高度：1500   默认最短距离：900   默认最长距离: 1200
    print(f"angle:{angle} height:{height} minL:{minl} maxl:{maxl}")

    point(data, angle, height)
