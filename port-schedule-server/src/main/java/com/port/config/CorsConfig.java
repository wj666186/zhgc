package com.port.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * 解决前端Vue(5173端口)访问后端8080跨域问题
 */
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                // 允许前端开发地址跨域
                .allowedOriginPatterns("http://localhost:5173")
                // 允许携带Cookie、凭证
                .allowCredentials(true)
                // 允许所有请求方式
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                // 预检请求有效期，单位秒
                .maxAge(3600);
    }
}