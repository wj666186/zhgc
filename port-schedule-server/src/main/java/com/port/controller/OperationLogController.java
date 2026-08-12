package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.OperationLog;
import com.port.service.OperationLogService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/log")
public class OperationLogController {

    @Resource
    private OperationLogService operationLogService;

    @GetMapping("/list")
    public Result<Page<OperationLog>> list(@RequestParam(defaultValue = "1") Integer pageNum,
                                           @RequestParam(defaultValue = "10") Integer pageSize,
                                           @RequestParam(required = false) String module,
                                           @RequestParam(required = false) String username,
                                           @RequestParam(required = false) Integer result) {
        LambdaQueryWrapper<OperationLog> wrapper = new LambdaQueryWrapper<>();
        if (module != null && !module.isBlank()) wrapper.eq(OperationLog::getModule, module);
        if (username != null && !username.isBlank()) wrapper.like(OperationLog::getUsername, username);
        if (result != null) wrapper.eq(OperationLog::getResult, result);
        wrapper.orderByDesc(OperationLog::getId);
        return Result.success(operationLogService.page(new Page<>(pageNum, pageSize), wrapper));
    }

    @GetMapping("/modules")
    public Result<List<String>> modules() {
        List<OperationLog> all = operationLogService.list();
        List<String> modules = all.stream()
                .map(OperationLog::getModule)
                .filter(m -> m != null && !m.isBlank())
                .distinct()
                .collect(Collectors.toList());
        return Result.success(modules);
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Long id) {
        return Result.success(operationLogService.removeById(id));
    }
}
