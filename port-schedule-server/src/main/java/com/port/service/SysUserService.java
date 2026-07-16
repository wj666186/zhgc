package com.port.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.port.domain.entity.SysUser;
import com.port.dto.UserDTO;
import java.util.List;

public interface SysUserService extends IService<SysUser> {
    // 查询全部用户
    List<SysUser> listAll();
    // 新增用户
    void addUser(UserDTO dto);
    // 修改用户
    void updateUser(UserDTO dto);
}