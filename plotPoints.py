import matplotlib.pyplot as plt
import math

lidarAngleStep = 0.125
lidarStartAngle = 0


def point(data, iHorizontalAngle, iHorizontalHeight):
    # 参与标定的帧数
    dataSize = len(data)
    minDistanceList = []
    plt.figure()

    # 获取对应距离的数据
    for idx, data_per_idx in enumerate(data):
        usedData = []
        for i, distance in enumerate(data_per_idx):
            # 保证1.2m-3.5m是路面
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

        x = [l for l, h in usedData]
        y = [h for l, h in usedData]
        plt.scatter(x, y, s=0.5)
        plt.pause(0.5)


if __name__ == '__main__':

    pass
