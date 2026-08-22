package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.QuayCrane;
import com.port.domain.entity.Rtg;
import com.port.service.QuayCraneService;
import com.port.service.RtgService;
import jakarta.annotation.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/equipment")
@PreAuthorize("authentication.principal.getRole() == 'admin' or authentication.principal.getRole() == 'operator'")
public class EquipmentController {

    @Resource
    private QuayCraneService quayCraneService;
    @Resource
    private RtgService rtgService;

    // ========== 岸桥 ==========
    @GetMapping("/crane/list")
    public Result<Page<QuayCrane>> craneList(@RequestParam(defaultValue = "1") Integer pageNum,
                                             @RequestParam(defaultValue = "10") Integer pageSize,
                                             @RequestParam(required = false) String craneNo,
                                             @RequestParam(required = false) Integer status) {
        LambdaQueryWrapper<QuayCrane> wrapper = new LambdaQueryWrapper<>();
        if (craneNo != null && !craneNo.isBlank()) wrapper.like(QuayCrane::getCraneNo, craneNo);
        if (status != null) wrapper.eq(QuayCrane::getStatus, status);
        wrapper.orderByDesc(QuayCrane::getId);
        return Result.success(quayCraneService.page(new Page<>(pageNum, pageSize), wrapper));
    }

    @GetMapping("/crane/all")
    public Result<List<QuayCrane>> craneAll() {
        return Result.success(quayCraneService.list());
    }

    @PostMapping("/crane/add")
    public Result<Boolean> craneAdd(@RequestBody QuayCrane crane) {
        return Result.success(quayCraneService.save(crane));
    }

    @PutMapping("/crane/update")
    public Result<Boolean> craneUpdate(@RequestBody QuayCrane crane) {
        return Result.success(quayCraneService.updateById(crane));
    }

    @DeleteMapping("/crane/{id}")
    public Result<Boolean> craneDelete(@PathVariable Long id) {
        return Result.success(quayCraneService.removeById(id));
    }

    @PostMapping("/crane/start")
    public Result<Boolean> craneStart(@RequestBody Map<String, Object> params) {
        Long id = Long.valueOf(params.get("id").toString());
        String vessel = params.getOrDefault("currentVessel", "").toString();
        QuayCrane crane = quayCraneService.getById(id);
        if (crane == null) return Result.fail("岸桥不存在");
        crane.setStatus(2);
        crane.setCurrentVessel(vessel);
        return Result.success(quayCraneService.updateById(crane));
    }

    @PutMapping("/crane/finish/{id}")
    public Result<Boolean> craneFinish(@PathVariable Long id) {
        QuayCrane crane = quayCraneService.getById(id);
        if (crane == null) return Result.fail("岸桥不存在");
        crane.setStatus(1);
        crane.setCurrentVessel(null);
        return Result.success(quayCraneService.updateById(crane));
    }

    @PostMapping("/crane/fault")
    public Result<Boolean> craneFault(@RequestBody Map<String, Object> params) {
        Long id = Long.valueOf(params.get("id").toString());
        String faultDesc = params.getOrDefault("faultDesc", "设备故障").toString();
        QuayCrane crane = quayCraneService.getById(id);
        if (crane == null) return Result.fail("岸桥不存在");
        crane.setStatus(3);
        crane.setFaultDesc(faultDesc);
        return Result.success(quayCraneService.updateById(crane));
    }

    @PostMapping("/crane/heartbeat/{id}")
    public Result<Boolean> craneHeartbeat(@PathVariable Long id) {
        QuayCrane crane = quayCraneService.getById(id);
        if (crane == null) return Result.fail("岸桥不存在");
        crane.setLastHeartbeat(LocalDateTime.now());
        return Result.success(quayCraneService.updateById(crane));
    }

    // ========== 龙门吊 ==========
    @GetMapping("/rtg/list")
    public Result<Page<Rtg>> rtgList(@RequestParam(defaultValue = "1") Integer pageNum,
                                     @RequestParam(defaultValue = "10") Integer pageSize,
                                     @RequestParam(required = false) String rtgNo,
                                     @RequestParam(required = false) Integer status) {
        LambdaQueryWrapper<Rtg> wrapper = new LambdaQueryWrapper<>();
        if (rtgNo != null && !rtgNo.isBlank()) wrapper.like(Rtg::getRtgNo, rtgNo);
        if (status != null) wrapper.eq(Rtg::getStatus, status);
        wrapper.orderByDesc(Rtg::getId);
        return Result.success(rtgService.page(new Page<>(pageNum, pageSize), wrapper));
    }

    @GetMapping("/rtg/all")
    public Result<List<Rtg>> rtgAll() {
        return Result.success(rtgService.list());
    }

    @PostMapping("/rtg/add")
    public Result<Boolean> rtgAdd(@RequestBody Rtg rtg) {
        return Result.success(rtgService.save(rtg));
    }

    @PutMapping("/rtg/update")
    public Result<Boolean> rtgUpdate(@RequestBody Rtg rtg) {
        return Result.success(rtgService.updateById(rtg));
    }

    @DeleteMapping("/rtg/{id}")
    public Result<Boolean> rtgDelete(@PathVariable Long id) {
        return Result.success(rtgService.removeById(id));
    }

    @PostMapping("/rtg/start")
    public Result<Boolean> rtgStart(@RequestBody Map<String, Object> params) {
        Long id = Long.valueOf(params.get("id").toString());
        String containerNo = params.getOrDefault("containerNo", "").toString();
        Rtg rtg = rtgService.getById(id);
        if (rtg == null) return Result.fail("龙门吊不存在");
        rtg.setStatus(2);
        rtg.setCurrentContainerNo(containerNo);
        return Result.success(rtgService.updateById(rtg));
    }

    @PutMapping("/rtg/finish/{id}")
    public Result<Boolean> rtgFinish(@PathVariable Long id) {
        Rtg rtg = rtgService.getById(id);
        if (rtg == null) return Result.fail("龙门吊不存在");
        rtg.setStatus(1);
        rtg.setCurrentContainerNo(null);
        return Result.success(rtgService.updateById(rtg));
    }

    @PostMapping("/rtg/fault")
    public Result<Boolean> rtgFault(@RequestBody Map<String, Object> params) {
        Long id = Long.valueOf(params.get("id").toString());
        String faultDesc = params.getOrDefault("faultDesc", "设备故障").toString();
        Rtg rtg = rtgService.getById(id);
        if (rtg == null) return Result.fail("龙门吊不存在");
        rtg.setStatus(3);
        rtg.setFaultDesc(faultDesc);
        return Result.success(rtgService.updateById(rtg));
    }

    @PostMapping("/rtg/heartbeat/{id}")
    public Result<Boolean> rtgHeartbeat(@PathVariable Long id) {
        Rtg rtg = rtgService.getById(id);
        if (rtg == null) return Result.fail("龙门吊不存在");
        rtg.setLastHeartbeat(LocalDateTime.now());
        return Result.success(rtgService.updateById(rtg));
    }
}
