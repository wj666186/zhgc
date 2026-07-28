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

    // 箱号
    private String containerNo;
    // 货物类型
    private String cargoType;
    // 目的港口
    private String destPort;
    // 重量
    private BigDecimal weight;

    /**
     * 集装箱整体业务状态
     * 0：待分配(绿色)
     * 1：已分配堆场
     * 2：破损锁定(橙色)
     * 3：已装船(蓝色)
     */
    private Integer status;

    // 关联具体仓位id
    private Long yardSlotId;

    /**
     * 所属堆场大区域：1 / 2 / 3
     */
    private Integer areaNo;

    /**
     * 装卸存放位置状态
     * 0：堆场内存放
     * 1：轮船货舱内（已装船）
     */
    private Integer loadStatus;

    // 3D场景X坐标
    private BigDecimal x;
    // 3D场景Z坐标
    private BigDecimal z;

    private LocalDateTime createTime;
    private LocalDateTime updateTime;
}
