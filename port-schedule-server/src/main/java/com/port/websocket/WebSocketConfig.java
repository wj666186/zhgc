package com.port.websocket;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        // 前端连接地址：ws://localhost:端口/ws/container
        registry.addHandler(new ContainerWebSocketServer(), "/ws/container")
                .setAllowedOrigins("*"); // 允许跨域访问
    }
}
