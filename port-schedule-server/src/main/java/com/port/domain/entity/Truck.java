package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("t_truck")
public class Truck implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;
    private String plateNo;
    private String driverName;
    private String driverPhone;
    private Integer truckType;
    private Integer status;
    private String currentContainerNo;
    private String startLocation;
    private String targetLocation;
    private BigDecimal longitude;
    private BigDecimal latitude;
    private Integer todayTaskCount;
    private BigDecimal totalMileage;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
