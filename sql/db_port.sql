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

CREATE TABLE t_ai_inspect (
                              id BIGINT AUTO_INCREMENT PRIMARY KEY,
                              container_no VARCHAR(20),
                              camera_id VARCHAR(30),
                              damage_level VARCHAR(10),
                              stack_status VARCHAR(20),
                              frame_url VARCHAR(255),
                              inspect_cost_ms INT,
                              create_time DATETIME DEFAULT NOW()
) ENGINE=InnoDB COMMENT='AI质检记录';

CREATE TABLE t_vessel_plan (
                               id BIGINT AUTO_INCREMENT PRIMARY KEY,
                               vessel_name VARCHAR(50),
                               berth_window_start DATETIME,
                               berth_window_end DATETIME,
                               total_container INT,
                               status VARCHAR(20),
                               create_time DATETIME DEFAULT NOW()
) ENGINE=InnoDB COMMENT='船舶靠泊计划';