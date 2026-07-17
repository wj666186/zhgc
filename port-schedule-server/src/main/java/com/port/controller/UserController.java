package com.port.controller;

import com.port.common.result.Result;
import com.port.domain.entity.SysUser;
import com.port.dto.UserDTO;
import com.port.service.SysUserService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private SysUserService sysUserService;

    /**
     * 查询用户列表
     * 仅管理员可访问
     */
    @GetMapping("/list")
    @PreAuthorize("authentication.principal.getRole() == 'admin'")
    public Result<List<SysUser>> getUserList() {
        return Result.success(sysUserService.listAll());
    }

    @PostMapping("/add")
    @PreAuthorize("authentication.principal.getRole() == 'admin'")
    public Result<Void> addUser(@RequestBody UserDTO dto) {
        sysUserService.addUser(dto);
        return Result.success(null);
    }

    @PutMapping("/update")
    @PreAuthorize("authentication.principal.getRole() == 'admin'")
    public Result<Void> updateUser(@RequestBody UserDTO dto) {
        sysUserService.updateUser(dto);
        return Result.success(null);
    }

    @DeleteMapping("/remove/{id}")
    @PreAuthorize("authentication.principal.getRole() == 'admin'")
    public Result<Void> deleteUser(@PathVariable Long id) {
        SysUser user = sysUserService.getById(id);
        if (user == null) {
            return Result.fail("目标用户不存在");
        }
        if ("admin".equals(user.getUsername())) {
            return Result.fail("系统默认管理员admin禁止删除");
        }
        sysUserService.removeById(id);
        return Result.success(null);
    }

}
