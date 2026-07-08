package com.port.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("t_container")
public class Container {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 箱号 */
    private String containerNo;

    /** 货物类型 */
    private String cargoType;

    /** 目的港口 */
    private String destPort;

    /** 重量 */
    private BigDecimal weight;

    /**
     * 0 待分配
     * 1 已分配堆场
     * 2 破损锁定
     */
    private Integer status;

    /** 绑定堆场仓位ID */
    private Long yardSlotId;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}