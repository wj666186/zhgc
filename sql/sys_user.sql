USE db_port;
CREATE TABLE `sys_user` (
                            `id` BIGINT AUTO_INCREMENT COMMENT '主键id',
                            `username` VARCHAR(50) NOT NULL COMMENT '登录用户名',
                            `password` VARCHAR(100) NOT NULL COMMENT 'BCrypt加密后的密码',
                            `role` VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '用户角色：admin管理员 / user普通用户',
                            `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                            PRIMARY KEY (`id`),
                            UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户账号表';
INSERT INTO sys_user (username, password, role)
VALUES (
           'admin',
           '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTHA6cHouL5QcoLMq7gp2pzXtD2',
           'admin'
       );

INSERT INTO sys_user (username, password, role)
VALUES
    (
        'user01',
        '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTHA6cHouL5QcoLMq7gp2pzXtD2',
        'user'
    ),
    (
        'user02',
        '$2a$10$7JB720yubVSZvUI0rEqK/.VqGOZTHA6cHouL5QcoLMq7gp2pzXtD2',
        'user'
    );
USE db_port;
UPDATE sys_user SET password = '123456' WHERE username = 'admin';
-- 另外两个测试账号一并改成明文密码
UPDATE sys_user SET password = '123456' WHERE username IN ('user01','user02');6696966