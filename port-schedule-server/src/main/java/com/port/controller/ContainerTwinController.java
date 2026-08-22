package com.port.controller;

import com.port.domain.entity.Container;
import com.port.domain.entity.YardSlot;

import com.port.service.ContainerService;
import com.port.service.YardSlotService;
import com.port.websocket.ContainerWebSocketServer;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/container/twin")
@CrossOrigin(origins = "*") // 解决前端跨域
@PreAuthorize("authentication.principal.getRole() == 'admin' or authentication.principal.getRole() == 'operator'")
public class ContainerTwinController {

    @Autowired
    private ContainerService containerService;
    @Autowired
    private YardSlotService yardSlotService;

    // 1. 查询所有集装箱数据（前端页面初始化加载）
    @GetMapping("/listContainer")
    public List<Container> getAllContainer() {
        return containerService.list();
    }

    // 2. 查询所有堆场仓位
    @GetMapping("/listSlot")
    public List<YardSlot> getAllSlot() {
        return yardSlotService.list();
    }

    // 3. 分配集装箱到指定堆场仓位
    @PutMapping("/assignSlot")
    public String assignSlot(@RequestParam Long containerId, @RequestParam Long slotId) {
        Container container = containerService.getById(containerId);
        // 破损箱子禁止分配仓位
        if (container.getStatus() == 2) {
            return "fail:破损锁定集装箱无法分配仓位";
        }
        container.setStatus(1);
        container.setYardSlotId(slotId);
        containerService.updateById(container);
        // 推送更新，两端页面刷新
        ContainerWebSocketServer.sendRefreshMsg();
        return "success";
    }

    // 4. 装载：堆场集装箱吊装上船（状态改为3已装船）
    @PutMapping("/loadToShip")
    public String loadToShip(@RequestParam Long containerId) {
        Container container = containerService.getById(containerId);
        // 仅堆场存放的箱子可以装船
        if (container.getStatus() != 1) {
            return "fail:只有堆场内集装箱才可装船";
        }
        container.setStatus(3);
        container.setYardSlotId(null);
        containerService.updateById(container);
        ContainerWebSocketServer.sendRefreshMsg();
        return "success";
    }

    // 5. 卸载：船上集装箱吊运至堆场指定仓位
    @PutMapping("/unloadFromShip")
    public String unloadFromShip(@RequestParam Long containerId, @RequestParam Long slotId) {
        Container container = containerService.getById(containerId);
        if (container.getStatus() != 3) {
            return "fail:只有船上集装箱才可卸载";
        }
        container.setStatus(1);
        container.setYardSlotId(slotId);
        containerService.updateById(container);
        ContainerWebSocketServer.sendRefreshMsg();
        return "success";
    }
}
