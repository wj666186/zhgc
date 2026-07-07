package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("t_container")
public class Container {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String containerNo;
    private String sizeType;
    private String cargoType;
    private Double weight;
    private String status;
    private String yardSlotCode;
    private String destPort;
    private Long vesselId;
    private Long aiInspectId;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;
    @TableField(fill = FieldFill.INSERT)
    private String createdBy;
    private String approvedBy;
    private String auditLog;
    @TableLogic
    private Integer deleted;
}