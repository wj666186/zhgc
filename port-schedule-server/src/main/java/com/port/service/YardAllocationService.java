package com.port.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.port.domain.entity.Container;
import com.port.domain.entity.YardSlot;
import com.port.mapper.ContainerMapper;
import com.port.mapper.YardSlotMapper;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class YardAllocationService {

    @Resource
    private ContainerMapper containerMapper;

    @Resource
    private YardSlotMapper yardSlotMapper;

    /**
     * 根据集装箱箱号，自动分配空闲堆场仓位
     * @param containerNo 集装箱箱号
     */
    @Transactional(rollbackFor = Exception.class)
    public void allocateYard(String containerNo) {
        // 入参非空校验
        if (containerNo == null || containerNo.trim().isEmpty()) {
            throw new RuntimeException("集装箱箱号不能为空");
        }

        // 1. 根据箱号查询集装箱详情
        LambdaQueryWrapper<Container> containerWrapper = new LambdaQueryWrapper<>();
        containerWrapper.eq(Container::getContainerNo, containerNo);
        Container container = containerMapper.selectOne(containerWrapper);

        if (container == null) {
            throw new RuntimeException("不存在该编号的集装箱");
        }
        // 破损锁定状态禁止分配仓位
        if (container.getStatus() == 2) {
            throw new RuntimeException("该集装箱已破损锁定，无法分配堆场");
        }
        // 已装船箱子不允许分配堆场
        if (container.getStatus() == 3) {
            throw new RuntimeException("已装船集装箱不可分配堆场仓位");
        }

        // 2. 查询任意一个未被占用的空闲仓位（未绑定集装箱）
        LambdaQueryWrapper<YardSlot> slotWrapper = new LambdaQueryWrapper<>();
        slotWrapper.isNull(YardSlot::getLockContainerId);
        YardSlot freeSlot = yardSlotMapper.selectOne(slotWrapper);

        if (freeSlot == null) {
            throw new RuntimeException("堆场暂无空闲仓位，分配失败");
        }

        // 3. 集装箱绑定仓位ID，状态改为已分配堆场
        container.setYardSlotId(freeSlot.getId());
        container.setStatus(1);
        containerMapper.updateById(container);

        // 4. 仓位锁定：绑定集装箱、占用层数+1
        freeSlot.setLockContainerId(container.getId());
        freeSlot.setUsedLayer(freeSlot.getUsedLayer() + 1);
        yardSlotMapper.updateById(freeSlot);
    }
}
