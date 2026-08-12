package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@TableName("t_gate_record")
public class GateRecord implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;
    private String passNo;
    private String gateNo;
    private Integer direction;
    private String plateNo;
    private String containerNo;
    private String appointmentNo;
    private Integer etcResult;
    private Integer rfidResult;
    private String ocrContainerNo;
    private Integer customsStatus;
    private Integer verifyStatus;
    private LocalDateTime enterTime;
    private LocalDateTime exitTime;
    private Integer stayMinutes;
    private String operator;
    private String remark;
    private LocalDateTime createTime;
}
