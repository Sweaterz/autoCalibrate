'''
Algorithm for calibration
用于自动标定的算法
'''
import math
import numpy as np

lidarAngleStep = 0.25


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
    for idx, data_per_idx in enumerate(data):
        usedData = []
        for i, distance in enumerate(data_per_idx):
            if 2060 <= distance <= 3640:
                angle = i * lidarAngleStep

                h = int(math.sin(math.radians(angle)) * distance)
                l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
                usedData.append([l, h])
            else:
                continue
        countNum = len(usedData) // 2
        for i in range(countNum):
            l1 = usedData[i]
            l2 = usedData[i + countNum]
            h1 = usedData[i]
            h2 = usedData[i + countNum]
            theta = math.atan((h1 - h2) / (l1 - l2)) / math.pi * 180
            usedData.append(theta)
        average = sum(usedData) / len(usedData)
        # 最大值和最小值之差应该满足小于0.5度
        while max(usedData) - min(usedData) > 0.5:
            diff = [math.fabs(data - average) for data in usedData]
            m = max(diff)
            index = diff.index(m)
            value = usedData[index]
            usedData.remove(value)
            average = sum(usedData) / len(usedData)
        thetaList.append(average)
    iHorizontalHeight = sum(thetaList) / len(thetaList)
    return iHorizontalHeight

def get_iHorizontalHeight(data, iHorizontalAngle):
    dataSize = len(data)
    heightList = []
    for idx, data_per_idx in enumerate(data):
        usedData = []
        for i, distance in enumerate(data_per_idx):
            # 保证1.2m-3.5m是路面
            if 2060 <= distance <= 3640:
                angle0 = i * lidarAngleStep
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

        heightList.append(sum(usedData) / len(usedData))

    iHorizontalHeight = sum(heightList) / len(heightList)
    return  iHorizontalHeight


def 




if __name__ == '__main__':
