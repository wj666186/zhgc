package com.port.controller;

import com.port.common.result.Result;
import com.port.dto.LoginDTO;
import com.port.dto.LoginVO;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api") // 统一添加接口前缀
public class LoginController {

    // 此时完整路径：/api/login，和前端请求地址完全对应
    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody LoginDTO loginDTO) {
        if ("admin".equals(loginDTO.getUsername()) && "123456".equals(loginDTO.getPassword())) {
            LoginVO vo = new LoginVO();
            vo.setToken(UUID.randomUUID().toString());
            vo.setUsername(loginDTO.getUsername());
            return Result.success(vo);
        } else {
            return Result.fail("用户名或密码错误");
        }
    }
}