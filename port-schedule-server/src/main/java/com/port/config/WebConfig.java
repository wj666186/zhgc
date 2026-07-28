package com.port.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import jakarta.annotation.Resource;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    // 直接注入容器里已经创建好的拦截器Bean
    @Resource
    private LoginInterceptor loginInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(loginInterceptor)
                .addPathPatterns("/**")
                .excludePathPatterns(
                        "/user/login",
                        "/api/container/twin",
                        "/api/container/load/ship/**",
                        "/api/container/unload/yard",
                        "/api/container/savePos",
                        "/ws/container/**"   // 放行WebSocket握手地址
                );
    }

}
