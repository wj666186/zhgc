package com.port.websocket;

import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.CopyOnWriteArraySet;

@Component
public class ContainerWebSocketServer extends TextWebSocketHandler {

    private static final Set<WebSocketSession> SESSION_LIST = new CopyOnWriteArraySet<>();
    private static final List<String> COMMAND_HISTORY = new ArrayList<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        SESSION_LIST.add(session);
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        SESSION_LIST.remove(session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) {
    }

    public static void sendRefreshMsg() {
        sendToAll("container_refresh");
    }

    public static void sendCommand(String command) {
        COMMAND_HISTORY.add(command);
        if (COMMAND_HISTORY.size() > 100) {
            COMMAND_HISTORY.remove(0);
        }
        sendToAll(command);
    }

    public static void sendToAll(String message) {
        for (WebSocketSession session : SESSION_LIST) {
            try {
                if (session.isOpen()) {
                    session.sendMessage(new TextMessage(message));
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    public static int getOnlineCount() {
        return SESSION_LIST.size();
    }

    public static List<String> getCommandHistory() {
        return new ArrayList<>(COMMAND_HISTORY);
    }
}
