package com.port.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.port.common.result.Result;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.servlet.HandlerInterceptor;

import java.io.PrintWriter;

public class LoginInterceptor implements HandlerInterceptor {

    // JSON序列化工具
    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 1. 跨域预检OPTIONS请求直接放行，必须放在最顶端
        if ("OPTIONS".equalsIgnoreCase(request.getMethod())) {
            response.setStatus(HttpServletResponse.SC_OK);
            return true;
        }

        String uri = request.getRequestURI();
        // 2. 精确匹配登录接口，直接放行
        if ("/api/login".equals(uri)) {
            return true;
        }

        // 3. 获取请求头Token
        String token = request.getHeader("Authorization");
        if (token == null || token.isBlank()) {
            // 设置返回JSON格式，前端能清晰识别未登录
            response.setContentType("application/json;charset=UTF-8");
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            PrintWriter writer = response.getWriter();
            // 返回统一失败Result
            Result<Object> failResult = Result.fail("未登录，请先登录");
            writer.write(objectMapper.writeValueAsString(failResult));
            writer.flush();
            writer.close();
            return false;
        }

        // Token存在，放行请求
        return true;
    }
}