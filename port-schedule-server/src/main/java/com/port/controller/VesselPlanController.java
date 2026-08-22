package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.VesselPlan;
import com.port.service.VesselPlanService;
import jakarta.annotation.Resource;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/vessel")
@PreAuthorize("authentication.principal.getRole() == 'admin' or authentication.principal.getRole() == 'operator'")
public class VesselPlanController {

    @Resource
    private VesselPlanService vesselPlanService;

    @GetMapping("/list")
    public Result<Page<VesselPlan>> list(@RequestParam(defaultValue = "1") Integer pageNum,
                                         @RequestParam(defaultValue = "10") Integer pageSize,
                                         @RequestParam(required = false) String vesselName,
                                         @RequestParam(required = false) Integer status) {
        LambdaQueryWrapper<VesselPlan> wrapper = new LambdaQueryWrapper<>();
        if (vesselName != null && !vesselName.isBlank()) wrapper.like(VesselPlan::getVesselName, vesselName);
        if (status != null) wrapper.eq(VesselPlan::getStatus, status);
        wrapper.orderByDesc(VesselPlan::getId);
        return Result.success(vesselPlanService.page(new Page<>(pageNum, pageSize), wrapper));
    }

    @GetMapping("/all")
    public Result<List<VesselPlan>> all() {
        return Result.success(vesselPlanService.list());
    }

    @PostMapping("/add")
    public Result<Boolean> add(@RequestBody VesselPlan vesselPlan) {
        return Result.success(vesselPlanService.save(vesselPlan));
    }

    @PutMapping("/update")
    public Result<Boolean> update(@RequestBody VesselPlan vesselPlan) {
        return Result.success(vesselPlanService.updateById(vesselPlan));
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Long id) {
        return Result.success(vesselPlanService.removeById(id));
    }

    @PutMapping("/berth/{id}")
    public Result<Boolean> berth(@PathVariable Long id) {
        VesselPlan vessel = vesselPlanService.getById(id);
        if (vessel == null) return Result.fail("船舶不存在");
        vessel.setStatus(1);
        vessel.setActualBerthTime(LocalDateTime.now());
        return Result.success(vesselPlanService.updateById(vessel));
    }

    @PutMapping("/finish/{id}")
    public Result<Boolean> finish(@PathVariable Long id) {
        VesselPlan vessel = vesselPlanService.getById(id);
        if (vessel == null) return Result.fail("船舶不存在");
        vessel.setStatus(2);
        vessel.setFinishedContainer(vessel.getTotalContainer());
        return Result.success(vesselPlanService.updateById(vessel));
    }

    @PutMapping("/departure/{id}")
    public Result<Boolean> departure(@PathVariable Long id) {
        VesselPlan vessel = vesselPlanService.getById(id);
        if (vessel == null) return Result.fail("船舶不存在");
        vessel.setStatus(3);
        vessel.setActualDepartureTime(LocalDateTime.now());
        return Result.success(vesselPlanService.updateById(vessel));
    }

    @PutMapping("/cancel/{id}")
    public Result<Boolean> cancel(@PathVariable Long id) {
        VesselPlan vessel = vesselPlanService.getById(id);
        if (vessel == null) return Result.fail("船舶不存在");
        vessel.setStatus(4);
        return Result.success(vesselPlanService.updateById(vessel));
    }
}
