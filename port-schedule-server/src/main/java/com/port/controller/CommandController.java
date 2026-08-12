package com.port.controller;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.port.common.result.Result;
import com.port.websocket.ContainerWebSocketServer;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/api/command")
public class CommandController {

    public static final String CMD_CRANE_LIFT = "crane_lift";
    public static final String CMD_CRANE_PLACE = "crane_place";
    public static final String CMD_TRUCK_PICKUP = "truck_pickup";
    public static final String CMD_TRUCK_DELIVER = "truck_deliver";
    public static final String CMD_RTG_MOVE = "rtg_move";
    public static final String CMD_ALERT = "alert";
    public static final String CMD_BROADCAST = "broadcast";

    @Resource
    private ObjectMapper objectMapper;

    private String toJson(Map<String, Object> map) {
        try {
            return objectMapper.writeValueAsString(map);
        } catch (Exception e) {
            return map.toString();
        }
    }

    @PostMapping("/send")
    public Result<Map<String, Object>> sendCommand(@RequestBody Map<String, Object> params) {
        String target = params.get("target").toString();
        String commandType = params.get("commandType").toString();
        String content = params.get("content").toString();
        String operator = params.getOrDefault("operator", "system").toString();
        Map<String, Object> message = new LinkedHashMap<>();
        message.put("id", System.currentTimeMillis());
        message.put("type", "command");
        message.put("target", target);
        message.put("commandType", commandType);
        message.put("content", content);
        message.put("operator", operator);
        message.put("timestamp", System.currentTimeMillis());
        message.put("createTime", new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        ContainerWebSocketServer.sendCommand(toJson(message));
        return Result.success(message);
    }

    @PostMapping("/broadcast")
    public Result<Map<String, Object>> broadcast(@RequestBody Map<String, Object> params) {
        String content = params.get("content").toString();
        Map<String, Object> message = new LinkedHashMap<>();
        message.put("id", System.currentTimeMillis());
        message.put("type", "broadcast");
        message.put("content", content);
        message.put("operator", "system");
        message.put("timestamp", System.currentTimeMillis());
        message.put("createTime", new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        ContainerWebSocketServer.sendCommand(toJson(message));
        return Result.success(message);
    }

    @PostMapping("/alert")
    public Result<Map<String, Object>> alert(@RequestBody Map<String, Object> params) {
        String level = params.getOrDefault("level", "warning").toString();
        String content = params.get("content").toString();
        Map<String, Object> message = new LinkedHashMap<>();
        message.put("id", System.currentTimeMillis());
        message.put("type", "alert");
        message.put("level", level);
        message.put("content", content);
        message.put("operator", "system");
        message.put("timestamp", System.currentTimeMillis());
        message.put("createTime", new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        ContainerWebSocketServer.sendCommand(toJson(message));
        return Result.success(message);
    }

    @GetMapping("/online/count")
    public Result<Integer> onlineCount() {
        return Result.success(ContainerWebSocketServer.getOnlineCount());
    }

    @GetMapping("/history")
    public Result<List<Map<String, Object>>> history() {
        List<String> rawList = ContainerWebSocketServer.getCommandHistory();
        List<Map<String, Object>> result = new ArrayList<>();
        for (String raw : rawList) {
            try {
                Map<String, Object> item = objectMapper.readValue(raw, new TypeReference<Map<String, Object>>() {});
                result.add(item);
            } catch (Exception e) {
                // 兼容旧的Java toString格式，尝试手动解析
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("content", raw);
                item.put("type", "unknown");
                result.add(item);
            }
        }
        // 倒序排列，最新的在前
        Collections.reverse(result);
        return Result.success(result);
    }
}
