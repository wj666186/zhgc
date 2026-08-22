USE db_port;
CREATE TABLE IF NOT EXISTS `sys_user` (
                            `id` BIGINT AUTO_INCREMENT COMMENT '主键id',
                            `username` VARCHAR(50) NOT NULL COMMENT '登录用户名',
                            `password` VARCHAR(100) NOT NULL COMMENT '密码',
                            `role` VARCHAR(20) NOT NULL DEFAULT 'operator' COMMENT '用户角色：admin管理员 / operator调度员',
                            `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                            PRIMARY KEY (`id`),
                            UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户账号表';

-- 两个角色测试账号，密码均为 123456
INSERT INTO sys_user (username, password, role) VALUES
    ('admin', '123456', 'admin'),
    ('operator', '123456', 'operator')
ON DUPLICATE KEY UPDATE role = VALUES(role);
