package com.port.controller;

import com.port.common.result.Result;
import com.port.domain.entity.SysUser;
import com.port.dto.UserDTO;
import com.port.service.SysUserService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

// 关键修改：@RequestMapping("/api/user") 补齐/api前缀
@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private SysUserService sysUserService;

    /**
     * 仅管理员可访问
     * PreAuthorize 校验登录用户角色必须是admin
     */
    @GetMapping("/list")
    @PreAuthorize("authentication.principal.role == 'admin'")
    public Result<List<SysUser>> getUserList() {
        return Result.success(sysUserService.listAll());
    }

    @PostMapping("/add")
    @PreAuthorize("authentication.principal.role == 'admin'")
    public Result<Void> addUser(@RequestBody UserDTO dto) {
        sysUserService.addUser(dto);
        return Result.success(null);
    }

    @PutMapping("/update")
    @PreAuthorize("authentication.principal.role == 'admin'")
    public Result<Void> updateUser(@RequestBody UserDTO dto) {
        sysUserService.updateUser(dto);
        return Result.success(null);
    }
}