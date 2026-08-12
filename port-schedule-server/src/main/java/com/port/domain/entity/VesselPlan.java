package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@TableName("t_vessel_plan")
public class VesselPlan implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;
    private String vesselName;
    private String imoNo;
    private String shippingCompany;
    private String routeLine;
    private LocalDateTime berthWindowStart;
    private LocalDateTime berthWindowEnd;
    private LocalDateTime actualBerthTime;
    private LocalDateTime actualDepartureTime;
    private Integer totalContainer;
    private Integer finishedContainer;
    private String berthNo;
    private Integer status;
    private String operator;
    private String remark;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
