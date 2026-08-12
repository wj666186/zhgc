package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.VesselPlan;
import com.port.mapper.VesselPlanMapper;
import com.port.service.VesselPlanService;
import org.springframework.stereotype.Service;

@Service
public class VesselPlanServiceImpl extends ServiceImpl<VesselPlanMapper, VesselPlan> implements VesselPlanService {
}
