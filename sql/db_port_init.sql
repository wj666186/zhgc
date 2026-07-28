-- 创建数据库
CREATE DATABASE IF NOT EXISTS db_port DEFAULT CHARACTER SET utf8mb4;
USE db_port;

-- 集装箱表（新增 area_no、load_status 两个字段，适配装卸业务）
DROP TABLE IF EXISTS t_container;
CREATE TABLE t_container(
                            id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
                            container_no VARCHAR(32) NOT NULL COMMENT '箱号',
                            cargo_type VARCHAR(64) COMMENT '货物类型',
                            dest_port VARCHAR(64) COMMENT '目的港口',
                            weight DECIMAL(10,2) COMMENT '重量',
                            status TINYINT DEFAULT 0 COMMENT '0待分配 1已分配堆场 2破损锁定 3已装船',
                            yard_slot_id BIGINT NULL COMMENT '绑定堆场ID',
    -- 新增字段：三大仓位编号 1/2/3
                            area_no INT NULL COMMENT '所属大仓位：1、2、3，船上时为空',
    -- 新增字段：存放位置状态
                            load_status TINYINT DEFAULT 0 COMMENT '0=堆场内  1=轮船货舱内',
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

-- 插入4条测试集装箱数据
INSERT INTO t_container
(container_no, cargo_type, dest_port, weight, status, yard_slot_id, area_no, load_status, create_time, update_time)
VALUES
    ('TNU1234567','电子设备','上海港',22.50,0,1,1,0,NOW(),NOW()),
    ('TNU1234568','日用百货','深圳港',18.20,2,2,2,0,NOW(),NOW()),
    ('TNU1234569','工业机械','宁波港',35.80,1,3,3,0,NOW(),NOW()),
    ('TNU1234570','钢材原料','天津港',42.00,3,null,null,1,NOW(),NOW());
-- 集装箱表新增三维摆放坐标字段

