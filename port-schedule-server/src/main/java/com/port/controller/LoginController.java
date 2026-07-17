package com.port.controller;

import com.port.common.result.Result;
import com.port.dto.LoginDTO;
import com.port.dto.LoginVO;
import com.port.security.LoginUser;
import jakarta.annotation.Resource;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/api")
public class LoginController {

    @Resource
    private AuthenticationManager authenticationManager;

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    @PostMapping("/login")
    public Result<LoginVO> login(@RequestBody LoginDTO loginDTO) {
        // 1. 封装账号密码认证
        UsernamePasswordAuthenticationToken authToken =
                new UsernamePasswordAuthenticationToken(loginDTO.getUsername(), loginDTO.getPassword());
        // 2. 认证校验
        Authentication authentication = authenticationManager.authenticate(authToken);

        // 3. 获取封装好的LoginUser对象
        LoginUser loginUser = (LoginUser) authentication.getPrincipal();

        // 4. 生成唯一令牌
        String token = UUID.randomUUID().toString().replace("-", "");

        // 5. Token作为key，LoginUser存入Redis，有效期30分钟
        redisTemplate.opsForValue().set("login:token:" + token, loginUser, 30, TimeUnit.MINUTES);

        // 6. 封装返回前端数据
        LoginVO vo = new LoginVO();
        vo.setToken(token);
        vo.setUsername(loginUser.getSysUser().getUsername());
        vo.setRole(loginUser.getSysUser().getRole());

        return Result.success(vo);
    }
}
