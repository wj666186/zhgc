package com.port.controller;

import org.springframework.beans.factory.annotation.Autowired;
import com.port.common.result.Result;
import com.port.domain.entity.AiInspectRecord;
import com.port.dto.AiInspectRequest;
import com.port.dto.AiInspectVO;
import com.port.service.AiInspectRecordService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.math.BigDecimal;
@RestController
@RequestMapping("/api/ai")
public class AiInspectController {

    @Autowired
    private AiInspectRecordService aiInspectRecordService;

    @PostMapping("/recognize")
    public Result<AiInspectVO> recognize(@RequestBody AiInspectRequest request) throws InterruptedException {
        long start = System.currentTimeMillis();
        Thread.sleep(2000);

        String containerNo = request.getContainerNo();
        if (containerNo == null || containerNo.isBlank()) {
            containerNo = "CNTU000001";
        }

        String inspectNo = "AI-" + System.currentTimeMillis();
        AiInspectVO vo = new AiInspectVO();
        vo.setInspectNo(inspectNo);
        vo.setContainerNo(containerNo);
        vo.setImageName(request.getImageName());
        vo.setDamageResult("疑似破损");
        vo.setDamageLevel("轻微");
        vo.setConfidence(0.9400000000000001);
        vo.setCostMs(System.currentTimeMillis() - start);

        // 存入数据库
        AiInspectRecord record = new AiInspectRecord();
        record.setInspectNo(inspectNo);
        record.setContainerNo(containerNo);
        record.setImageName(request.getImageName());
        record.setDamageResult(vo.getDamageResult());
        record.setDamageLevel(vo.getDamageLevel());
        record.setConfidence(new BigDecimal("0.9400000000000001"));
        record.setCostMs((int) (System.currentTimeMillis() - start));
        aiInspectRecordService.save(record);

        return Result.success(vo);
    }
}