package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.Rtg;
import com.port.mapper.RtgMapper;
import com.port.service.RtgService;
import org.springframework.stereotype.Service;

@Service
public class RtgServiceImpl extends ServiceImpl<RtgMapper, Rtg> implements RtgService {
}
