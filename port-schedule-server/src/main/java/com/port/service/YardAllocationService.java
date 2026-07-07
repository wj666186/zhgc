package com.port.service;

import com.port.domain.entity.Container;
import com.port.domain.entity.YardSlot;
import com.port.mapper.ContainerMapper;
import com.port.mapper.YardSlotMapper;
import lombok.RequiredArgsConstructor;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
@RequiredArgsConstructor
public class YardAllocationService {
    private final YardSlotMapper slotMapper;
    private final ContainerMapper containerMapper;
    private final RedissonClient redissonClient;

    @Transactional(rollbackFor = Exception.class)
    public void autoAllocateSlot(String containerNo) {
        RLock lock = redissonClient.getLock("yard_allocate_lock");
        try {
            lock.lock();
            Container container = containerMapper.selectByContainerNo(containerNo);
            List<YardSlot> idleSlots = slotMapper.selectIdleByRule(container.getDestPort(), container.getCargoType(), container.getWeight());
            if (!idleSlots.isEmpty()) {
                YardSlot bestSlot = idleSlots.get(0);
                container.setYardSlotCode(bestSlot.getSlotCode());
                container.setStatus("YARD_STORAGE");
                containerMapper.updateById(container);
                bestSlot.setOccupied(1);
                slotMapper.updateById(bestSlot);
            }
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    public void lockDamageContainer(String containerNo) {
        Container container = containerMapper.selectByContainerNo(containerNo);
        container.setStatus("DAMAGE_FORBID_LOAD");
        containerMapper.updateById(container);
    }
}