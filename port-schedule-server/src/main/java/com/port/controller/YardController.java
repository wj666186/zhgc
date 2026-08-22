package com.port.controller;

import com.port.common.result.Result;
import com.port.domain.entity.YardSlot;
import com.port.mapper.YardSlotMapper;
import com.port.service.YardAllocationService;
import jakarta.annotation.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

// 增加 /api 统一前缀，和前端请求路径匹配
@RestController
@RequestMapping("/api/yard")
@PreAuthorize("authentication.principal.getRole() == 'admin' or authentication.principal.getRole() == 'operator'")
public class YardController {

    @Resource
    private YardAllocationService yardAllocationService;

    @Resource
    private YardSlotMapper yardSlotMapper;

    /**
     * 根据箱号分配堆场
     * 前端地址：POST /api/yard/allocate?containerNo=xxx
     */
    @PostMapping("/allocate")
    public Result<String> allocate(@RequestParam String containerNo){
        yardAllocationService.allocateYard(containerNo);
        return Result.success("堆场分配完成");
    }

    /**
     * 查询所有堆场仓位列表（前端必备接口，解决500报错）
     * 前端地址：GET /api/yard/list
     */
    @GetMapping("/list")
    public Result<List<YardSlot>> listAllYardSlot(){
        List<YardSlot> slotList = yardSlotMapper.selectList(null);
        return Result.success(slotList);
    }
}
