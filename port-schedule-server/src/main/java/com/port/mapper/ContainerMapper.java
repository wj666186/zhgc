package com.port.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.port.domain.entity.Container;
import org.apache.ibatis.annotations.Param;

public interface ContainerMapper extends BaseMapper<Container> {
    Container selectByContainerNo(@Param("boxNo") String boxNo);
}