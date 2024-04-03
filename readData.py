import os
import socket



def chooseDataDG():
    use_data = []
    with open(filePath, 'r') as fopen:
        lines = fopen.readlines()
        for idx, line in enumerate(lines):
            line_data = line.split(" ")
            if line_data[0] != 'FC':
                continue
            if line_data[4] =='9D' and line_data[5] =='03':
                if len(line_data) < 925:
                    print('this scan data is not enough, discard it!')
                    continue
            elif line_data[4] == '0D' and line_data[5] == '07':
                if len(line_data) < 1813:
                    print('this scan data is not enough, discard it!')
                    continue
            lidarAngleStep = (int(line_data[24], 16) + int(line_data[25], 16) * 256) / 10000
            num_points = int(line_data[19], 16) * 256 + int(line_data[18], 16)
            # assert num_points * 2 + 49 - 1 == 1810
            use_data.append(line_data[49: 2 * num_points + 49])
    return use_data

def readDatDG():
    use_data = chooseDataDG()

    if len(use_data) < 30:
        print("this data is not right! please check it! filePath is %s" % filePath)
        return all_data
    # 标定开始
    iHorizontalAngle, iHorizontalHeight, min_l, max_l = standardization_dg(use_data[10], lidarAngleStep, up2down)
    if up2down:
        coefficient = -1
    else:
        coefficient = 1
    # 标定结束
    for idx, data in enumerate(use_data):
        size = len(data)
        for i in range(int(size / 2)):
            MSB = data[i * 2 + 1]
            LSB = data[i * 2]
            distance = int(MSB, 16) * 256 + int(LSB, 16)
            if distance < 100:
                continue
            angle0 = i * lidarAngleStep
            # h = int(math.sin(math.radians(angle0)) * distance) + iHorizontalHeight
            # l = int(math.cos(math.fabs(angle0) * math.pi / 180) * distance)
            if angle0 < iHorizontalAngle:
                angle = iHorizontalAngle - angle0
                h = iHorizontalHeight - int(math.sin(math.radians(angle)) * distance) * coefficient
                l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
            elif angle0 > iHorizontalAngle:
                angle = angle0 - self.iHorizontalAngle
                h = iHorizontalHeight + int(math.sin(math.radians(angle)) * distance) * coefficient
                l = int(math.cos(math.fabs(angle) * math.pi / 180) * distance)
            else:
                h = iHorizontalHeight
                l = distance
            # if 300 < l < 6000 and 5000 > h > 0:  # if l > 300 and l < 4000 and  h < 5000 and h > 0:
            #     if self.start_idx == 0:
            #         self.start_idx = idx
            end_idx = idx
            # if idx > 150:
            #     all_data.append([idx, l / 20.0, h / 20.0, 150])  # all_data.append([idx, h, l, 150, i])
            # if self.min_l < l < self.max_l:
            #     self.all_data.append([idx, l / 20.0, h / 20.0, 150])
            if l < 6000:
                all_data.append([idx, l / 20.0, h / 20.0, 150])

    print("read format: the file:%s, start_idx:%d, end_idx:%d" % (filePath, start_idx, end_idx))
    if savePath is not "":
        savedir = "/".join(savePath.split('/')[:-1])
        if not os.path.exists(savedir):  # 如果路径不存在
            os.makedirs(savedir)
        binpc = np.array(all_data)
        binpc = binpc.reshape(-1, 4).astype(np.float32)
        binpc.tofile(savePath)
    return all_data


if __name__ == '__main__':
    cs = socket()
    cs.connect()
