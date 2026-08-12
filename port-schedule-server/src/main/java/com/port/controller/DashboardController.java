package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.port.common.result.Result;
import com.port.domain.entity.*;
import com.port.service.*;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    @Resource private ContainerService containerService;
    @Resource private TruckService truckService;
    @Resource private GateRecordService gateRecordService;
    @Resource private VesselPlanService vesselPlanService;
    @Resource private QuayCraneService quayCraneService;
    @Resource private RtgService rtgService;
    @Resource private AiInspectRecordService aiInspectRecordService;

    @GetMapping("/stats")
    public Result<Map<String, Object>> stats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("containerTotal", containerService.count());
        stats.put("containerNormal", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 0)));
        stats.put("containerWorking", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 1)));
        stats.put("containerDamage", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 2)));
        stats.put("truckTotal", truckService.count());
        stats.put("truckIdle", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 0)));
        stats.put("truckWorking", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 1)));
        stats.put("vesselTotal", vesselPlanService.count());
        stats.put("vesselWorking", vesselPlanService.count(new LambdaQueryWrapper<VesselPlan>().eq(VesselPlan::getStatus, 1)));
        stats.put("craneTotal", quayCraneService.count());
        stats.put("craneWorking", quayCraneService.count(new LambdaQueryWrapper<QuayCrane>().eq(QuayCrane::getStatus, 2)));
        stats.put("rtgTotal", rtgService.count());
        stats.put("aiTotal", aiInspectRecordService.count());
        return Result.success(stats);
    }

    @GetMapping("/container/status")
    public Result<List<Map<String, Object>>> containerStatus() {
        List<Map<String, Object>> list = new ArrayList<>();
        list.add(Map.of("name", "正常", "value", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 0))));
        list.add(Map.of("name", "作业中", "value", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 1))));
        list.add(Map.of("name", "破损", "value", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 2))));
        list.add(Map.of("name", "已装船", "value", containerService.count(new LambdaQueryWrapper<Container>().eq(Container::getStatus, 3))));
        return Result.success(list);
    }

    @GetMapping("/truck/status")
    public Result<List<Map<String, Object>>> truckStatus() {
        List<Map<String, Object>> list = new ArrayList<>();
        list.add(Map.of("name", "空闲", "value", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 0))));
        list.add(Map.of("name", "运输中", "value", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 1))));
        list.add(Map.of("name", "装卸中", "value", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 2))));
        list.add(Map.of("name", "维修中", "value", truckService.count(new LambdaQueryWrapper<Truck>().eq(Truck::getStatus, 3))));
        return Result.success(list);
    }

    @GetMapping("/equipment/oee")
    public Result<List<Map<String, Object>>> equipmentOee() {
        List<Map<String, Object>> list = new ArrayList<>();
        List<QuayCrane> cranes = quayCraneService.list(new LambdaQueryWrapper<QuayCrane>().orderByDesc(QuayCrane::getOee).last("LIMIT 10"));
        for (QuayCrane c : cranes) {
            Map<String, Object> m = new HashMap<>();
            m.put("name", c.getCraneNo());
            m.put("oee", c.getOee() != null ? c.getOee() : 0);
            list.add(m);
        }
        return Result.success(list);
    }

    @GetMapping("/throughput/trend")
    public Result<List<Map<String, Object>>> throughputTrend() {
        List<Map<String, Object>> list = new ArrayList<>();
        for (int i = 6; i >= 0; i--) {
            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.DAY_OF_MONTH, -i);
            String date = String.format("%02d-%02d", cal.get(Calendar.MONTH)+1, cal.get(Calendar.DAY_OF_MONTH));
            list.add(Map.of("date", date, "value", (int)(Math.random()*500+200)));
        }
        return Result.success(list);
    }

    @GetMapping("/gate/efficiency")
    public Result<List<Map<String, Object>>> gateEfficiency() {
        List<Map<String, Object>> list = new ArrayList<>();
        String[] gates = {"G1", "G2", "G3", "G4"};
        for (String g : gates) {
            list.add(Map.of("gate", g, "pass", (int)(Math.random()*100+50), "plan", 150));
        }
        return Result.success(list);
    }

    @GetMapping("/vessel/top")
    public Result<List<Map<String, Object>>> vesselTop() {
        List<VesselPlan> vessels = vesselPlanService.list(new LambdaQueryWrapper<VesselPlan>().orderByDesc(VesselPlan::getTotalContainer).last("LIMIT 10"));
        List<Map<String, Object>> list = vessels.stream().map(v -> {
            Map<String, Object> m = new HashMap<>();
            m.put("name", v.getVesselName());
            m.put("total", v.getTotalContainer() != null ? v.getTotalContainer() : 0);
            return m;
        }).collect(Collectors.toList());
        return Result.success(list);
    }
}
