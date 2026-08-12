package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.io.Serializable;
import java.time.LocalDateTime;

@Data
@TableName("t_operation_log")
public class OperationLog implements Serializable {
    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.AUTO)
    private Long id;
    private String logNo;
    private String username;
    private String userRole;
    private String module;
    private String operation;
    private String description;
    private String requestMethod;
    private String requestUrl;
    private String requestParams;
    private String ipAddress;
    private Integer result;
    private String errorMsg;
    private Long costMs;
    private LocalDateTime createTime;
}
