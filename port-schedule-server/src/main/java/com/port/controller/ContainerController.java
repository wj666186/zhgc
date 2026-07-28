package com.port.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.Container;
import com.port.dto.ContainerPosDTO;
import com.port.service.ContainerService;
import com.port.websocket.ContainerWebSocketServer;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;

@RestController
@RequestMapping("/api/container")
public class ContainerController {

    // 注入Service层，标准三层架构
    @Resource
    private ContainerService containerService;

    /**
     * 分页查询集装箱列表（后台表格页面）
     */
    @GetMapping("/list")
    public Result<IPage<Container>> list(
            @RequestParam(defaultValue = "1") Long pageNum,
            @RequestParam(defaultValue = "10") Long pageSize
    ){
        Page<Container> page = new Page<>(pageNum, pageSize);
        IPage<Container> pageData = containerService.page(page, null);
        return Result.success(pageData);
    }

    /**
     * 数字孪生3D视图专用：查询全部集装箱
     * 底层Service清空MyBatis缓存，每次读取数据库最新坐标、状态
     */
    @GetMapping("/twin")
    public Result<List<Container>> getAllContainerForTwin() {
        List<Container> allList = containerService.listAll();
        return Result.success(allList);
    }

    /**
     * 拖拽松开保存坐标接口
     */
    @PostMapping("/savePos")
    public Result<Void> saveContainerPosition(@RequestBody ContainerPosDTO dto) {
        // 打印接收参数，调试用
        System.out.println("接收拖拽坐标：id="+dto.getId()+" x="+dto.getX()+" z="+dto.getZ());
        BigDecimal x = dto.getX();
        BigDecimal z = dto.getZ();
        containerService.updateContainerPos(dto.getId(), x, z);
        ContainerWebSocketServer.sendRefreshMsg();
        return Result.success(null);
    }

    /**
     * 新增集装箱
     */
    @PostMapping("/add")
    public Result<Void> add(@RequestBody Container container){
        container.setStatus(0);
        container.setAreaNo(1);
        container.setLoadStatus(0);
        // 初始坐标
        container.setX(BigDecimal.ZERO);
        container.setZ(BigDecimal.ZERO);
        containerService.save(container);
        ContainerWebSocketServer.sendRefreshMsg();
        return Result.success(null);
    }

    /**
     * 编辑集装箱基础信息
     */
    @PutMapping("/update")
    public Result<Void> update(@RequestBody Container container){
        containerService.updateById(container);
        ContainerWebSocketServer.sendRefreshMsg();
        return Result.success(null);
    }

    /**
     * 删除集装箱
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id){
        containerService.removeById(id);
        ContainerWebSocketServer.sendRefreshMsg();
        return Result.success(null);
    }

    /**
     * 标记集装箱破损
     */
    @PutMapping("/damage")
    public Result<String> damage(@RequestBody Container container){
        container.setStatus(2);
        containerService.updateById(container);
        ContainerWebSocketServer.sendRefreshMsg();
        return Result.success("标记损坏成功");
    }

    // ============ 装卸3D拖拽业务接口 ============
    /**
     * 装船：堆场箱子吊运至船上
     * 不再强制覆盖坐标，永久保留拖拽摆放位置
     */
    @PutMapping("/load/ship/{id}")
    public Result<Void> loadToShip(@PathVariable Long id){
        containerService.loadShip(id);
        return Result.success(null);
    }

    /**
     * 卸船：船上箱子放回指定堆场分区
     * 仅修改业务状态，坐标完全保留拖拽落地位置
     */
    @PostMapping("/unload/yard")
    public Result<Void> unloadToYard(
            @RequestParam Long id,
            @RequestParam Integer areaNo
    ){
        if (areaNo < 1 || areaNo > 3) {
            return Result.fail("仅支持选择1、2、3号区域");
        }
        containerService.unLoadYard(id, areaNo);
        return Result.success(null);
    }
}
