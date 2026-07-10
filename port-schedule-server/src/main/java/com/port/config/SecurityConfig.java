package com.port.config;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                // 关闭csrf
                .csrf(csrf -> csrf.disable())
                // 关闭默认登录跳转页面（核心！禁止302重定向）
                .formLogin(form -> form.disable())
                // 放行所有请求，不再做登录拦截
                .authorizeHttpRequests(auth -> auth.anyRequest().permitAll());
        return http.build();
    }
}