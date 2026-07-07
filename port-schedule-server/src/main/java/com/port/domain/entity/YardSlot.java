package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("t_yard_slot")
public class YardSlot {
    private Long id;
    private String slotCode;
    private String areaCode;
    private Integer rowNo;
    private Integer colNo;
    private Integer maxLayer;
    private Integer occupied;
    private String forbiddenCargo;
}