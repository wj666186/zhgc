package com.port.controller;

import com.port.common.result.Result;
import com.port.dto.LoginDTO;
import com.port.dto.LoginVO;
import com.port.security.LoginUser;
import jakarta.annotation.Resource;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api")
public class LoginController {

    @Resource
    private AuthenticationManager authenticationManager;

    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody LoginDTO loginDTO) {
        // 1. 封装账号密码到认证对象
        UsernamePasswordAuthenticationToken authToken =
                new UsernamePasswordAuthenticationToken(loginDTO.getUsername(), loginDTO.getPassword());
        // 2. 调用Security自动从sys_user表查询并校验密码
        Authentication authentication = authenticationManager.authenticate(authToken);
        System.out.println("前端收到用户名："+loginDTO.getUsername());
        System.out.println("前端收到原始密码：【"+loginDTO.getPassword()+"】");
        // 注入Security认证管理器
        // 3. 获取登录用户信息（包含角色role）
        LoginUser loginUser = (LoginUser) authentication.getPrincipal();
        // 4. 生成Token
        String token = UUID.randomUUID().toString();
        System.out.println("前端接收密码："+loginDTO.getPassword());
        // 5. 封装返回VO，携带用户名+角色+令牌
        LoginVO vo = new LoginVO();
        vo.setToken(token);
        vo.setUsername(loginUser.getSysUser().getUsername());
        vo.setRole(loginUser.getSysUser().getRole());

        return Result.success(vo);
    }
}