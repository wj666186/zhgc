package com.port.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.port.domain.entity.YardSlot;
import org.apache.ibatis.annotations.Param;
import java.util.List;

public interface YardSlotMapper extends BaseMapper<YardSlot> {
    List<YardSlot> selectIdleByRule(@Param("dest") String destPort,
                                    @Param("cargo") String cargoType,
                                    @Param("weight") Double weight);
}