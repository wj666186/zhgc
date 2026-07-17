package com.port.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.port.common.result.Result;
import com.port.security.LoginUser;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;
import jakarta.annotation.Resource;
import java.io.PrintWriter;
import java.util.concurrent.TimeUnit;

@Component
public class LoginInterceptor implements HandlerInterceptor {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 1. 跨域OPTIONS预检请求直接放行
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return true;
        }

        // 2. 登录接口直接放行
        String uri = request.getRequestURI();
        if ("/api/login".equals(uri)) {
            return true;
        }

        // 3. 获取请求头Token
        String token = request.getHeader("Authorization");
        if (token == null || token.isBlank()) {
            return writeFailResponse(response, "未登录，请先登录");
        }

        // 4. 根据Token从Redis取出登录用户信息
        String redisKey = "login:token:" + token;
        LoginUser loginUser = (LoginUser) redisTemplate.opsForValue().get(redisKey);
        if (loginUser == null) {
            return writeFailResponse(response, "登录已过期，请重新登录");
        }

        // 5. 将完整LoginUser认证信息存入Security上下文
        UsernamePasswordAuthenticationToken authToken
                = new UsernamePasswordAuthenticationToken(loginUser, null, loginUser.getAuthorities());
        SecurityContextHolder.getContext().setAuthentication(authToken);

        // 6. 刷新Redis过期时长
        redisTemplate.expire(redisKey, 30, TimeUnit.MINUTES);

        return true;
    }

    /** 统一输出未登录JSON提示 */
    private boolean writeFailResponse(HttpServletResponse response, String msg) throws Exception {
        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        PrintWriter writer = response.getWriter();
        Result<Object> failResult = Result.fail(msg);
        writer.write(objectMapper.writeValueAsString(failResult));
        writer.flush();
        writer.close();
        return false;
    }
}
