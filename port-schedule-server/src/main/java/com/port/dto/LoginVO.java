package com.port.dto;

import lombok.Data;

@Data
public class LoginVO {
    private String token;
    private String username;
    // 用户角色 admin / operator
    private String role;
}
