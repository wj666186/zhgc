package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@TableName("t_quay_crane")
public class QuayCrane implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;
    private String craneNo;
    private String berthNo;
    private String model;
    private Integer status;
    private String operator;
    private String currentVessel;
    private Integer trolleyPosition;
    private Integer gantryPosition;
    private Double liftHeight;
    private Integer spreaderStatus;
    private Integer todayBoxCount;
    private Long totalBoxCount;
    private Double oee;
    private String faultDesc;
    private LocalDateTime lastHeartbeat;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
