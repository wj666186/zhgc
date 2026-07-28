package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.YardSlot;
import com.port.mapper.YardSlotMapper;
import com.port.service.YardSlotService;
import org.springframework.stereotype.Service;

@Service
public class YardSlotServiceImpl extends ServiceImpl<YardSlotMapper, YardSlot> implements YardSlotService {
}
