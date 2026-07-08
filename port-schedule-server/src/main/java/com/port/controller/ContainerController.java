package com.port.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.R;
import com.port.domain.entity.Container;
import com.port.mapper.ContainerMapper;
import org.springframework.web.bind.annotation.*;
import com.port.common.result.R;
import jakarta.annotation.Resource;

@RestController
@RequestMapping("/container")
public class ContainerController {

    @Resource
    private ContainerMapper containerMapper;

    /**
     * 分页查询集装箱列表
     */
    @GetMapping("/list")
    public R<IPage<Container>> list(
            @RequestParam(defaultValue = "1") Long pageNum,
            @RequestParam(defaultValue = "10") Long pageSize
    ){
        Page<Container> page = new Page<>(pageNum, pageSize);
        IPage<Container> pageData = containerMapper.selectPage(page, null);
        return R.ok(pageData);
    }

    /**
     * 标记集装箱损坏锁定
     */
    @PutMapping("/damage")
    public R<String> damage(@RequestBody Container container){
        // status 2 代表破损锁定
        container.setStatus(2);
        containerMapper.updateById(container);
        return R.ok("标记损坏成功");
    }
}