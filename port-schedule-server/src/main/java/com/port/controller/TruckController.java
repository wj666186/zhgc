package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.Truck;
import com.port.service.TruckService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/truck")
public class TruckController {

    @Resource
    private TruckService truckService;

    @GetMapping("/list")
    public Result<Page<Truck>> list(@RequestParam(defaultValue = "1") Integer pageNum,
                                    @RequestParam(defaultValue = "10") Integer pageSize,
                                    @RequestParam(required = false) String plateNo,
                                    @RequestParam(required = false) Integer status) {
        LambdaQueryWrapper<Truck> wrapper = new LambdaQueryWrapper<>();
        if (plateNo != null && !plateNo.isBlank()) wrapper.like(Truck::getPlateNo, plateNo);
        if (status != null) wrapper.eq(Truck::getStatus, status);
        wrapper.orderByDesc(Truck::getId);
        Page<Truck> page = truckService.page(new Page<>(pageNum, pageSize), wrapper);
        return Result.success(page);
    }

    @GetMapping("/all")
    public Result<List<Truck>> all() {
        return Result.success(truckService.list());
    }

    @GetMapping("/idle")
    public Result<List<Truck>> idle() {
        LambdaQueryWrapper<Truck> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Truck::getStatus, 0);
        return Result.success(truckService.list(wrapper));
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("total", truckService.count());
        stats.put("idle", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 0)));
        stats.put("working", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 1)));
        stats.put("repair", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 3)));
        return Result.success(stats);
    }

    @PostMapping("/add")
    public Result<Boolean> add(@RequestBody Truck truck) {
        return Result.success(truckService.save(truck));
    }

    @PutMapping("/update")
    public Result<Boolean> update(@RequestBody Truck truck) {
        return Result.success(truckService.updateById(truck));
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Long id) {
        return Result.success(truckService.removeById(id));
    }

    @PostMapping("/assign")
    public Result<Boolean> assign(@RequestBody Map<String, Object> params) {
        Long truckId = Long.valueOf(params.get("truckId").toString());
        String containerNo = params.get("containerNo").toString();
        String targetLocation = params.get("targetLocation").toString();
        Truck truck = truckService.getById(truckId);
        if (truck == null) return Result.fail("集卡不存在");
        truck.setStatus(1);
        truck.setCurrentContainerNo(containerNo);
        truck.setTargetLocation(targetLocation);
        return Result.success(truckService.updateById(truck));
    }

    @PutMapping("/finish/{id}")
    public Result<Boolean> finish(@PathVariable Long id) {
        Truck truck = truckService.getById(id);
        if (truck == null) return Result.fail("集卡不存在");
        truck.setStatus(0);
        truck.setCurrentContainerNo(null);
        truck.setStartLocation(null);
        truck.setTargetLocation(null);
        truck.setTodayTaskCount(truck.getTodayTaskCount() + 1);
        return Result.success(truckService.updateById(truck));
    }

    @PostMapping("/gps")
    public Result<Boolean> gps(@RequestBody Map<String, Object> params) {
        Long truckId = Long.valueOf(params.get("truckId").toString());
        java.math.BigDecimal longitude = new java.math.BigDecimal(params.get("longitude").toString());
        java.math.BigDecimal latitude = new java.math.BigDecimal(params.get("latitude").toString());
        Truck truck = truckService.getById(truckId);
        if (truck == null) return Result.fail("集卡不存在");
        truck.setLongitude(longitude);
        truck.setLatitude(latitude);
        return Result.success(truckService.updateById(truck));
    }
}
