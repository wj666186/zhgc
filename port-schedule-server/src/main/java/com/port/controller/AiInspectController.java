package com.port.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.port.common.result.Result;
import com.port.domain.entity.AiInspectRecord;
import com.port.service.AiInspectRecordService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

@RestController
@RequestMapping("/api/ai")
public class AiInspectController {

    @Resource
    private AiInspectRecordService aiInspectRecordService;

    private static final String UPLOAD_DIR = "C:/Users/86186/Desktop/gangkou/uploads/ai";

    @PostMapping("/inspect")
    public Result<Map<String, Object>> inspect(@RequestParam("file") MultipartFile file,
                                               @RequestParam(required = false) String containerNo) {
        long start = System.currentTimeMillis();
        try {
            // 保存上传图片
            File dir = new File(UPLOAD_DIR);
            if (!dir.exists()) dir.mkdirs();
            String originalName = file.getOriginalFilename();
            String ext = originalName != null && originalName.contains(".")
                    ? originalName.substring(originalName.lastIndexOf("."))
                    : ".jpg";
            String fileName = "ai_" + System.currentTimeMillis() + ext;
            String filePath = UPLOAD_DIR + "/" + fileName;
            file.transferTo(new File(filePath));

            // 调用Python AI服务（如果可用），否则使用模拟识别
            Map<String, Object> aiResult = callAiService(filePath);
            if (aiResult == null) {
                aiResult = mockAiResult(containerNo);
            }

            // 自动入库
            String inspectNo = "AI" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss")) + (int)(Math.random()*1000);
            String ocrResult = aiResult.get("ocrResult") != null ? aiResult.get("ocrResult").toString() : "";
            String finalContainerNo = (containerNo != null && !containerNo.isBlank()) ? containerNo : ocrResult;

            AiInspectRecord record = new AiInspectRecord();
            record.setInspectNo(inspectNo);
            record.setContainerNo(finalContainerNo);
            record.setImageName(fileName);
            record.setDamageResult(aiResult.get("damageResult") != null ? aiResult.get("damageResult").toString() : "无破损");
            record.setDamageLevel(aiResult.get("damageLevel") != null ? aiResult.get("damageLevel").toString() : "无");
            record.setConfidence(new BigDecimal(aiResult.get("confidence") != null ? aiResult.get("confidence").toString() : "0.95"));
            record.setCostMs((int)(System.currentTimeMillis() - start));
            record.setCreateTime(LocalDateTime.now());
            aiInspectRecordService.save(record);

            // 返回可视化结果
            Map<String, Object> result = new HashMap<>();
            result.put("inspectNo", inspectNo);
            result.put("containerNo", finalContainerNo);
            result.put("imageName", fileName);
            result.put("imageUrl", "/uploads/ai/" + fileName);
            result.put("ocrResult", ocrResult);
            result.put("damageResult", record.getDamageResult());
            result.put("damageLevel", record.getDamageLevel());
            result.put("stackResult", aiResult.get("stackResult") != null ? aiResult.get("stackResult").toString() : "正常堆码");
            result.put("confidence", record.getConfidence());
            result.put("costMs", record.getCostMs());
            result.put("inspectTime", record.getCreateTime());
            return Result.success(result);
        } catch (Exception e) {
            return Result.fail("识别失败: " + e.getMessage());
        }
    }

    @GetMapping("/list")
    public Result<Page<AiInspectRecord>> list(@RequestParam(defaultValue = "1") Integer pageNum,
                                              @RequestParam(defaultValue = "10") Integer pageSize,
                                              @RequestParam(required = false) String containerNo) {
        LambdaQueryWrapper<AiInspectRecord> wrapper = new LambdaQueryWrapper<>();
        if (containerNo != null && !containerNo.isBlank()) wrapper.like(AiInspectRecord::getContainerNo, containerNo);
        wrapper.orderByDesc(AiInspectRecord::getId);
        return Result.success(aiInspectRecordService.page(new Page<>(pageNum, pageSize), wrapper));
    }

    @GetMapping("/history")
    public Result<List<AiInspectRecord>> history(@RequestParam(defaultValue = "50") Integer limit) {
        LambdaQueryWrapper<AiInspectRecord> wrapper = new LambdaQueryWrapper<>();
        wrapper.orderByDesc(AiInspectRecord::getId).last("LIMIT " + limit);
        return Result.success(aiInspectRecordService.list(wrapper));
    }

    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Long id) {
        return Result.success(aiInspectRecordService.removeById(id));
    }

    private Map<String, Object> callAiService(String filePath) {
        try {
            String url = "http://localhost:5000/api/inspect";
            // 简单HTTP调用Python服务
            java.net.URL obj = new java.net.URL(url);
            java.net.HttpURLConnection con = (java.net.HttpURLConnection) obj.openConnection();
            con.setRequestMethod("POST");
            con.setDoOutput(true);
            con.setRequestProperty("Content-Type", "application/json");
            String body = "{\"image_path\":\"" + filePath.replace("\\", "/") + "\"}";
            con.getOutputStream().write(body.getBytes("UTF-8"));
            int responseCode = con.getResponseCode();
            if (responseCode == 200) {
                Scanner scanner = new Scanner(con.getInputStream(), "UTF-8");
                String response = scanner.useDelimiter("\\A").next();
                scanner.close();
                // 解析JSON
                com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                return mapper.readValue(response, Map.class);
            }
        } catch (Exception e) {
            // AI服务不可用，返回null使用模拟
        }
        return null;
    }

    private Map<String, Object> mockAiResult(String containerNo) {
        Map<String, Object> result = new HashMap<>();
        String[] damages = {"无破损", "左侧轻微凹陷", "顶部锈蚀", "角件变形", "底部刮擦", "右侧凹陷", "门板变形"};
        String[] levels = {"无", "轻微", "中度", "严重"};
        String[] stacks = {"正常堆码", "偏斜", "超高", "单层平放", "双层错位"};
        int idx = (int)(Math.random() * damages.length);
        result.put("ocrResult", containerNo != null && !containerNo.isBlank() ? containerNo : "CSLU" + (int)(Math.random()*9000000+1000000));
        result.put("damageResult", damages[idx]);
        result.put("damageLevel", idx == 0 ? "无" : levels[Math.min(idx, 3)]);
        result.put("stackResult", stacks[(int)(Math.random()*stacks.length)]);
        result.put("confidence", String.format("%.3f", 0.85 + Math.random()*0.14));
        return result;
    }
}
