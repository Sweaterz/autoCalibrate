void ProcessScanData::parseDGData(std::vector<string> &hex_data, int &scan_idx)
{
    try {
        float intensity = 150.0;
        sensor::ScanData scan_data;
        int byteLen = int(std::stoi(hex_data[5], 0, 16) * 0x100 + std::stoi(hex_data[4], 0, 16));
        int hexSize = hex_data.size();
        // 剔除异常点云帧
        if (hex_data[0] != "FC" | hex_data[1] != "FD" | hex_data[2] != "FE" | hex_data[3] != "FF" | hexSize < byteLen + 8) {
            return;
        }
        if(hexSize > byteLen + 8){
            int deleteNum = hexSize - byteLen - 8;
            for (int i=0; i<deleteNum;i++) {
                sensor::deleteData<std::string>(hex_data, hex_data[hexSize - i - 1]);
            }
        }
        uint start_ = 49;
        uint num_points = int32_t(std::stoi(hex_data[19], 0, 16) * 0x100 + std::stoi(hex_data[18], 0, 16));
        uint end_ = num_points * 2 + start_;
        std::vector<std::string> scan_data_string;
        scan_data_string.reserve(num_points * 2);
        for (uint i = start_; i < end_; i++) {
            scan_data_string.push_back(hex_data[i]);
        }
        float angleStep = int32_t(std::stoi(hex_data[25], 0, 16) * 0x100 + std::stoi(hex_data[24], 0, 16)) / 10000.0;
        if(angleStep != dg_param.lidarAngleStep)
        {
            LOG_ERROR("lidarAngleStep in alg.cfg is not right, please check it! The program will exit! angleStep:" + std::to_string(angleStep) + " dg_param.lidarAngleStep:" + std::to_string(dg_param.lidarAngleStep));
            exit(-1);
        }
        const uint64_t timestamp = sensor::getTimeStampForMs();
        for (uint j = 0; j < num_points; j++) {
            uint distance = uint(std::stoi(scan_data_string[j * 2 + 1], 0, 16) * 0x100 + std::stoi(scan_data_string[j * 2], 0, 16));
            if (distance < 100.0) {
                continue;
            }
            float angle_ = 0.0;
            float h = 0.0;
            float l = 0.0;
            float angle = j * dg_param.lidarAngleStep;
            if(dg_param.scanningDirection == 0){
                if (angle < dg_param.iHorizontalAngle) {
                    angle_ = dg_param.iHorizontalAngle - angle;
                    h = dg_param.iHorizontalHeight + uint(sin(angle_ * M_PI / 180) * distance);
                    l = uint(cos(abs(angle_ * M_PI / 180)) * distance);
                } else if (angle > dg_param.iHorizontalAngle) {
                    angle_ = angle - dg_param.iHorizontalAngle;
                    h = dg_param.iHorizontalHeight - uint(sin(angle_ * M_PI / 180) * distance);
                    l = uint(cos(abs(angle_ * M_PI / 180)) * distance);
                } else {
                    h = dg_param.iHorizontalHeight;
                    l = distance;
                }
            }
            else {
                if (angle < dg_param.iHorizontalAngle) {
                    angle_ = dg_param.iHorizontalAngle - angle;
                    h = dg_param.iHorizontalHeight - uint(sin(angle_ * M_PI / 180) * distance);
                    l = uint(cos(abs(angle_ * M_PI / 180)) * distance);
                } else if (angle > dg_param.iHorizontalAngle) {
                    angle_ = angle - dg_param.iHorizontalAngle;
                    h = dg_param.iHorizontalHeight + uint(sin(angle_ * M_PI / 180) * distance);
                    l = uint(cos(abs(angle_ * M_PI / 180)) * distance);
                } else {
                    h = dg_param.iHorizontalHeight;
                    l = distance;
                }
            }

            if (l > dg_param.minDisForFilter && l < dg_param.maxDisForFilter && h > dg_param.minHeightForFilter && h < dg_param.maxHeightForFilter) {
                if(l <= dg_param.minDisForFilter + dg_param.widthOfIslandEdge && h <= dg_param.minHeightForFilter + dg_param.heightOfIslandEdge){
                    continue;
                }
                if(l <= dg_param.minDisForFilter + dg_param.widthOfWeighEdge + dg_param.widthOfIslandEdge && l > dg_param.minDisForFilter + dg_param.widthOfIslandEdge &&
                        h <= dg_param.minHeightForFilter + dg_param.heightOfWeighEdge && h > dg_param.minHeightForFilter){
                    continue;
                }
                scan_data.scan.push_back({float(scan_idx), l, h, intensity, timestamp, float(j)});
            }
        }
        scan_data.timestamp = timestamp;

        if (scan_data.scan.size() != 0) {
            AddScanData(scan_data);
        }
        else {
            sensor::ScanData scan_data_null;
            scan_data_null.scan.push_back({float(scan_idx), 500, 200, intensity, timestamp, 0});
            scan_data_null.timestamp = timestamp;
            AddScanData(scan_data_null);
        }
        scan_idx++;
        scan_data.clear();
    } catch (const char* msg) {
        std::cerr<<"parseDG error: "<<msg<<std::endl;
    }


}