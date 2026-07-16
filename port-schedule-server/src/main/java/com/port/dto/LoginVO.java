package com.port.dto;

import lombok.Data;

@Data
public class LoginVO {
    private String token;
    private String username;
    // 新增：用户角色 admin / user
    private String role;
}
