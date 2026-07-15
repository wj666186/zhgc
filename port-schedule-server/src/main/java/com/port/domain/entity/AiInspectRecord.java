package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("ai_inspect_record")
public class AiInspectRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    // 检测单号
    private String inspectNo;
    // 集装箱号
    private String containerNo;
    // 图片文件名
    private String imageName;
    // 破损描述
    private String damageResult;
    // 破损等级
    private String damageLevel;
    // 置信度
    private BigDecimal confidence;
    // 耗时
    private Integer costMs;
    // 创建时间
    private LocalDateTime createTime;
}