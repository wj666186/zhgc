package com.port.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.port.domain.entity.Container;

import java.math.BigDecimal;
import java.util.List;

/**
 * 集装箱业务顶层接口
 * 继承IService 获得MyBatis-Plus全套基础增删改查、分页方法
 */
public interface ContainerService extends IService<Container> {

    /**
     * 查询全部集装箱列表
     */
    List<Container> listAll();

    /**
     * 根据箱号查询单个集装箱
     * @param boxNo 箱号
     * @return 集装箱实体
     */
    Container selectByContainerNo(String boxNo);

    /**
     * 更新拖拽坐标
     * @param id 主键id
     * @param x X坐标
     * @param z Z坐标
     */
    void updateContainerPos(Long id, BigDecimal x, BigDecimal z);

    /**
     * 集装箱装船
     * @param id 集装箱id
     */
    void loadShip(Long id);

    /**
     * 集装箱卸船分配堆场区域
     * @param id 集装箱id
     * @param areaNo 区域编号
     */
    void unLoadYard(Long id, Integer areaNo);
}
