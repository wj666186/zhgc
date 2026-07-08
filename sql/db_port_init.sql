-- 创建数据库
CREATE DATABASE IF NOT EXISTS db_port DEFAULT CHARACTER SET utf8mb4;
USE db_port;

-- 集装箱表
DROP TABLE IF EXISTS t_container;
CREATE TABLE t_container(
                            id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
                            container_no VARCHAR(32) NOT NULL COMMENT '箱号',
                            cargo_type VARCHAR(64) COMMENT '货物类型',
                            dest_port VARCHAR(64) COMMENT '目的港口',
                            weight DECIMAL(10,2) COMMENT '重量',
                            status TINYINT DEFAULT 0 COMMENT '0待分配 1已分配堆场 2破损锁定',
                            yard_slot_id BIGINT NULL COMMENT '绑定堆场ID',
                            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                            update_time DATETIME ON UPDATE CURRENT_TIMESTAMP
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='集装箱';

-- 堆场仓位表
DROP TABLE IF EXISTS t_yard_slot;
CREATE TABLE t_yard_slot(
                            id BIGINT AUTO_INCREMENT PRIMARY KEY,
                            area_code VARCHAR(8) NOT NULL COMMENT '堆场分区 A/B/C',
                            row_no INT NOT NULL COMMENT '排',
                            col_no INT NOT NULL COMMENT '列',
                            max_layer INT DEFAULT 3 COMMENT '最大层数',
                            used_layer INT DEFAULT 0 COMMENT '已占用层数',
                            lock_container_id BIGINT NULL COMMENT '占用集装箱ID'
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='堆场仓位';

-- 初始化3个堆场空位
INSERT INTO t_yard_slot(area_code,row_no,col_no) VALUES
                                                     ('A',1,1),
                                                     ('A',1,2),
                                                     ('A',1,3);

-- 插入测试集装箱数据
INSERT INTO t_container(container_no,cargo_type,dest_port,weight,status)
VALUES
    ('CNTU000001','电子产品','新加坡',26.5,0),
    ('CNTU000002','五金钢材','马来西亚',27.2,0),
    ('CNTU000003','日用百货','泰国',25.8,0);