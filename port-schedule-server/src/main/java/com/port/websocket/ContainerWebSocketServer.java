package com.port.websocket;

import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArraySet;

public class ContainerWebSocketServer extends TextWebSocketHandler {

    // 存放所有前端在线WebSocket会话
    private static final Set<WebSocketSession> SESSION_LIST = new CopyOnWriteArraySet<>();

    // 客户端建立WebSocket连接
    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        SESSION_LIST.add(session);
    }

    // 客户端关闭页面/断开连接
    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        SESSION_LIST.remove(session);
    }

    // 无需接收前端上行消息，空实现
    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
    }

    /**
     * 静态全局广播：推送集装箱刷新指令给所有在线前端
     */
    public static void sendRefreshMsg() {
        final String pushMsg = "container_refresh";
        for (WebSocketSession session : SESSION_LIST) {
            try {
                if (session.isOpen()) {
                    session.sendMessage(new TextMessage(pushMsg));
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }
}
