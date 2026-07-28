package com.port.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.Container;
import com.port.mapper.ContainerMapper;
import com.port.service.ContainerService;
import com.port.websocket.ContainerWebSocketServer;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.ibatis.session.SqlSession;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Slf4j
@Service
public class ContainerServiceImpl extends ServiceImpl<ContainerMapper, Container>
        implements ContainerService {

    @Resource
    private ContainerMapper containerMapper;

    @Resource
    private SqlSession sqlSession;

    /**
     * 查询所有集装箱，清空一级缓存，每次读取数据库最新数据
     */
    @Override
    public List<Container> listAll() {
        sqlSession.clearCache();
        return containerMapper.selectList(null);
    }

    @Override
    public Container selectByContainerNo(String boxNo) {
        return containerMapper.selectByContainerNo(boxNo);
    }

    /**
     * 拖拽坐标更新：仅更新X、Z坐标，不推送WebSocket
     * 业务状态变更(装船/卸船)才统一推送一次全局刷新
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void updateContainerPos(Long id, BigDecimal x, BigDecimal z) {
        log.info("开始更新箱体坐标，箱体ID：{}，X坐标：{}，Z坐标：{}", id, x, z);
        int affectRows = containerMapper.savePosition(id, x, z);
        log.info("坐标更新执行完成，数据库受影响行数：{}", affectRows);
        // ========= 删除这行：坐标更新无需推送刷新 =========
        // ContainerWebSocketServer.sendRefreshMsg();
    }

    /**
     * 装船业务：调用自定义SQL
     * load_status=1、area_no置空、自动刷新update_time
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void loadShip(Long id) {
        Container container = getById(id);
        if (container == null) {
            log.warn("箱体不存在，ID：{}", id);
            return;
        }
        // 执行Mapper注解SQL统一更新字段
        int rows = containerMapper.loadShip(id);
        log.info("集装箱装船完成，ID:{}, 影响行数:{}", id, rows);
        // WebSocket推送刷新（唯一一次推送）
        ContainerWebSocketServer.sendRefreshMsg();
    }

    /**
     * 卸船回堆场：load_status=0，回填区域编号，自动更新时间
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void unLoadYard(Long id, Integer areaNo) {
        Container container = getById(id);
        if (container == null) {
            log.warn("箱体不存在，ID：{}", id);
            return;
        }
        int rows = containerMapper.unLoadYard(id, areaNo);
        log.info("集装箱卸船完成，ID:{},区域编号:{},影响行数:{}", id, areaNo, rows);
        // WebSocket推送刷新（唯一一次推送）
        ContainerWebSocketServer.sendRefreshMsg();
    }
}
