package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.QuayCrane;
import com.port.mapper.QuayCraneMapper;
import com.port.service.QuayCraneService;
import org.springframework.stereotype.Service;

@Service
public class QuayCraneServiceImpl extends ServiceImpl<QuayCraneMapper, QuayCrane> implements QuayCraneService {
}
