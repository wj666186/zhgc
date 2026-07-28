package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

@Data
@TableName("t_yard_slot")
public class YardSlot {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String areaCode;
    private Integer rowNo;
    private Integer colNo;
    private Integer maxLayer;
    private Integer usedLayer;
    private Long lockContainerId;
}
