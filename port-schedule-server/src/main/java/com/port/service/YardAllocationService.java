package com.port.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.port.domain.entity.Container;
import com.port.domain.entity.YardSlot;
import com.port.mapper.ContainerMapper;
import com.port.mapper.YardSlotMapper;
import org.springframework.stereotype.Service;
import jakarta.annotation.Resource;

@Service
public class YardAllocationService {

    @Resource
    private ContainerMapper containerMapper;

    @Resource
    private YardSlotMapper yardSlotMapper;

    /**
     * 根据箱号分配空闲堆场
     */
    public void allocateYard(String containerNo){
        // 1. 查询集装箱
        LambdaQueryWrapper<Container> conWrap = new LambdaQueryWrapper<>();
        conWrap.eq(Container::getContainerNo, containerNo);
        Container container = containerMapper.selectOne(conWrap);
        if(container == null){
            throw new RuntimeException("不存在该集装箱");
        }
        if(container.getStatus() == 2){
            throw new RuntimeException("该集装箱已破损锁定，禁止分配");
        }

        // 2. 查询第一个空闲仓位
        LambdaQueryWrapper<YardSlot> slotWrap = new LambdaQueryWrapper<>();
        slotWrap.isNull(YardSlot::getLockContainerId);
        YardSlot freeSlot = yardSlotMapper.selectOne(slotWrap);
        if(freeSlot == null){
            throw new RuntimeException("当前无空闲堆场仓位");
        }

        // 3. 绑定仓位
        container.setYardSlotId(freeSlot.getId());
        container.setStatus(1);
        containerMapper.updateById(container);

        // 4. 仓位锁定
        freeSlot.setLockContainerId(container.getId());
        freeSlot.setUsedLayer(freeSlot.getUsedLayer() + 1);
        yardSlotMapper.updateById(freeSlot);
    }
}