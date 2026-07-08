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

    /** 堆场分区 A/B/C */
    private String areaCode;

    /** 排号 */
    private Integer rowNo;

    /** 列号 */
    private Integer colNo;

    /** 最大堆叠层数 */
    private Integer maxLayer;

    /** 当前已占用层数 */
    private Integer usedLayer;

    /** 占用该仓位的集装箱ID */
    private Long lockContainerId;
}