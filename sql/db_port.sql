CREATE DATABASE IF NOT EXISTS db_port DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE db_port;

CREATE TABLE `t_container` (
                               id BIGINT AUTO_INCREMENT PRIMARY KEY,
                               container_no VARCHAR(20) NOT NULL COMMENT '集装箱唯一箱号',
                               size_type VARCHAR(10),
                               cargo_type VARCHAR(20),
                               weight DOUBLE,
                               status VARCHAR(20),
                               yard_slot_code VARCHAR(20),
                               dest_port VARCHAR(30),
                               vessel_id BIGINT,
                               ai_inspect_id BIGINT,
                               created_by VARCHAR(50),
                               approved_by VARCHAR(50),
                               audit_log TEXT,
                               create_time DATETIME DEFAULT NOW(),
                               update_time DATETIME DEFAULT NOW() ON UPDATE NOW(),
                               deleted TINYINT DEFAULT 0,
                               UNIQUE uk_container_no(container_no)
) ENGINE=InnoDB COMMENT='集装箱信息';

CREATE TABLE t_yard_slot (
                             id BIGINT AUTO_INCREMENT PRIMARY KEY,
                             slot_code VARCHAR(20) NOT NULL COMMENT '箱位编号 A01-03-02',
                             area_code VARCHAR(10),
                             row_no INT, col_no INT, max_layer INT,
                             occupied TINYINT DEFAULT 0,
                             forbidden_cargo VARCHAR(100),
                             UNIQUE uk_slot_code(slot_code)
) ENGINE=InnoDB COMMENT='堆场箱位';

CREATE TABLE `ai_inspect_record` (
                                     id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键id',
                                     inspect_no VARCHAR(64) NOT NULL UNIQUE COMMENT '检测单号',
                                     container_no VARCHAR(32) NOT NULL COMMENT '集装箱编号',
                                     image_name VARCHAR(128) COMMENT '图片文件名',
                                     damage_result VARCHAR(256) COMMENT '破损描述',
                                     damage_level VARCHAR(16) COMMENT '破损等级',
                                     confidence DECIMAL(18,16) COMMENT '置信度',
                                     cost_ms INT COMMENT '接口耗时ms',
                                     create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI集装箱破损检测记录表';

CREATE TABLE t_vessel_plan (
                               id BIGINT AUTO_INCREMENT PRIMARY KEY,
                               vessel_name VARCHAR(50),
                               berth_window_start DATETIME,
                               berth_window_end DATETIME,
                               total_container INT,
                               status VARCHAR(20),
                               create_time DATETIME DEFAULT NOW()
) ENGINE=InnoDB COMMENT='船舶靠泊计划';