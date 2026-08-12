package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.OperationLog;
import com.port.mapper.OperationLogMapper;
import com.port.service.OperationLogService;
import org.springframework.stereotype.Service;

@Service
public class OperationLogServiceImpl extends ServiceImpl<OperationLogMapper, OperationLog> implements OperationLogService {
}
