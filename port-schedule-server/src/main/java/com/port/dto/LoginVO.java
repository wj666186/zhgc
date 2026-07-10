package com.port.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
// 无参构造，保证 new LoginVO() 可用
@NoArgsConstructor
// 全参构造，支持 new LoginVO(token, username)
@AllArgsConstructor
public class LoginVO {
    private String token;
    private String username;
}