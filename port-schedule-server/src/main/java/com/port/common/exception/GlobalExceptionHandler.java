package com.port.common.exception;

import com.port.common.result.R;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

/**
 * 全局统一异常捕获处理器
 */
@ControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 捕获系统所有未被捕获的异常
     */
    @ExceptionHandler(Exception.class)
    @ResponseBody
    public R<String> handleException(Exception e){
        // 控制台打印异常堆栈，方便排查问题
        e.printStackTrace();
        // 向前端返回统一格式错误信息
        return R.fail(e.getMessage());
    }
}