package com.port.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.Container;
import com.port.mapper.ContainerMapper;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("api/container")
public class ContainerController {

    @Resource
    private ContainerMapper containerMapper;

    /**
     * 分页查询集装箱列表
     */
    @GetMapping("/list")
    public Result<IPage<Container>> list(
            @RequestParam(defaultValue = "1") Long pageNum,
            @RequestParam(defaultValue = "10") Long pageSize
    ){
        Page<Container> page = new Page<>(pageNum, pageSize);
        IPage<Container> pageData = containerMapper.selectPage(page, null);
        return Result.success(pageData);
    }
    /**
     * 新增集装箱
     */
    @PostMapping("/add")
    public Result<Void> add(@RequestBody Container container){
        // 默认状态为0 正常
        container.setStatus(0);
        containerMapper.insert(container);
        return Result.success(null);
    }
    /**
     * 编辑修改集装箱信息
     */
    @PutMapping("/update")
    public Result<Void> update(@RequestBody Container container){
        containerMapper.updateById(container);
        return Result.success(null);
    }

    /**
     * 根据id删除单条集装箱
     */
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id){
        containerMapper.deleteById(id);
        return Result.success(null);
    }

    /**
     * 标记集装箱损坏锁定
     */
    @PutMapping("/damage")
    public Result<String> damage(@RequestBody Container container){
        // status 2 代表破损锁定
        container.setStatus(2);
        containerMapper.updateById(container);
        return Result.success("标记损坏成功");
    }
}