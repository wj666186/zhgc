package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.GateRecord;
import com.port.service.GateRecordService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/gate")
public class GateRecordController {

    @Resource
    private GateRecordService gateRecordService;

    @GetMapping("/list")
    public Result<Page<GateRecord>> list(@RequestParam(defaultValue = "1") Integer pageNum,
                                         @RequestParam(defaultValue = "10") Integer pageSize,
                                         @RequestParam(required = false) String plateNo,
                                         @RequestParam(required = false) String containerNo,
                                         @RequestParam(required = false) Integer direction,
                                         @RequestParam(required = false) Integer verifyStatus) {
        LambdaQueryWrapper<GateRecord> wrapper = new LambdaQueryWrapper<>();
        if (plateNo != null && !plateNo.isBlank()) wrapper.like(GateRecord::getPlateNo, plateNo);
        if (containerNo != null && !containerNo.isBlank()) wrapper.like(GateRecord::getContainerNo, containerNo);
        if (direction != null) wrapper.eq(GateRecord::getDirection, direction);
        if (verifyStatus != null) wrapper.eq(GateRecord::getVerifyStatus, verifyStatus);
        wrapper.orderByDesc(GateRecord::getId);
        return Result.success(gateRecordService.page(new Page<>(pageNum, pageSize), wrapper));
    }

    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        Map<String, Object> stats = new HashMap<>();
        LocalDateTime todayStart = LocalDateTime.now().withHour(0).withMinute(0).withSecond(0);
        stats.put("todayTotal", gateRecordService.count(new LambdaQueryWrapper<GateRecord>().ge(GateRecord::getCreateTime, todayStart)));
        stats.put("todayPass", gateRecordService.count(new LambdaQueryWrapper<GateRecord>().ge(GateRecord::getCreateTime, todayStart).eq(GateRecord::getVerifyStatus, 1)));
        stats.put("todayFail", gateRecordService.count(new LambdaQueryWrapper<GateRecord>().ge(GateRecord::getCreateTime, todayStart).eq(GateRecord::getVerifyStatus, 2)));
        stats.put("inPort", gateRecordService.count(new LambdaQueryWrapper<GateRecord>().eq(GateRecord::getDirection, 1).isNull(GateRecord::getExitTime)));
        return Result.success(stats);
    }

    @PostMapping("/verify")
    public Result<GateRecord> verify(@RequestBody Map<String, Object> params) {
        String plateNo = params.get("plateNo").toString();
        String containerNo = params.get("containerNo").toString();
        String appointmentNo = params.getOrDefault("appointmentNo", "").toString();
        String passNo = "GATE" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss")) + (int)(Math.random()*1000);
        GateRecord record = new GateRecord();
        record.setPassNo(passNo);
        record.setGateNo("G1");
        record.setDirection(1);
        record.setPlateNo(plateNo);
        record.setContainerNo(containerNo);
        record.setAppointmentNo(appointmentNo);
        record.setEtcResult(1);
        record.setRfidResult(1);
        record.setOcrContainerNo(containerNo);
        record.setCustomsStatus(1);
        record.setVerifyStatus(1);
        record.setEnterTime(LocalDateTime.now());
        record.setOperator("系统自动核验");
        gateRecordService.save(record);
        return Result.success(record);
    }

    @PutMapping("/exit/{id}")
    public Result<Boolean> exit(@PathVariable Long id) {
        GateRecord record = gateRecordService.getById(id);
        if (record == null) return Result.fail("记录不存在");
        record.setExitTime(LocalDateTime.now());
        if (record.getEnterTime() != null) {
            record.setStayMinutes((int) java.time.Duration.between(record.getEnterTime(), LocalDateTime.now()).toMinutes());
        }
        return Result.success(gateRecordService.updateById(record));
    }

    @GetMapping("/pass/{passNo}")
    public Result<GateRecord> getByPassNo(@PathVariable String passNo) {
        LambdaQueryWrapper<GateRecord> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(GateRecord::getPassNo, passNo);
        return Result.success(gateRecordService.getOne(wrapper));
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Long id) {
        return Result.success(gateRecordService.removeById(id));
    }
}
