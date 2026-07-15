package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.AiInspectRecord;
import com.port.mapper.AiInspectRecordMapper;
import com.port.service.AiInspectRecordService;
import org.springframework.stereotype.Service;

@Service
public class AiInspectRecordServiceImpl
        extends ServiceImpl<AiInspectRecordMapper, AiInspectRecord>
        implements AiInspectRecordService {
}