package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.Truck;
import com.port.mapper.TruckMapper;
import com.port.service.TruckService;
import org.springframework.stereotype.Service;

@Service
public class TruckServiceImpl extends ServiceImpl<TruckMapper, Truck> implements TruckService {
}
