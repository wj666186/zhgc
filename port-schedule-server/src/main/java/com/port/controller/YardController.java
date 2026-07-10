package com.port.controller;

import com.port.common.result.Result;
import com.port.domain.entity.Container;
import com.port.service.YardAllocationService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import jakarta.annotation.Resource;

@RestController
@RequestMapping("/yard")

public class YardController {

    @Resource
    private YardAllocationService yardAllocationService;

    /**
     * 自动分配堆场
     */
    @PostMapping("/allocate")
    public Result<String> allocate(@RequestBody Container container){
        yardAllocationService.allocateYard(container.getContainerNo());
        return Result.success("堆场分配完成");
    }
}