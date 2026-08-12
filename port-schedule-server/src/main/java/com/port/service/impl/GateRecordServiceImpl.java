package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.GateRecord;
import com.port.mapper.GateRecordMapper;
import com.port.service.GateRecordService;
import org.springframework.stereotype.Service;

@Service
public class GateRecordServiceImpl extends ServiceImpl<GateRecordMapper, GateRecord> implements GateRecordService {
}
