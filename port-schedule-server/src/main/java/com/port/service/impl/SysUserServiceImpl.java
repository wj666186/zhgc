package com.port.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.port.domain.entity.SysUser;
import com.port.dto.UserDTO;
import com.port.mapper.SysUserMapper;
import com.port.service.SysUserService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

@Service
public class SysUserServiceImpl extends ServiceImpl<SysUserMapper, SysUser>
        implements SysUserService {

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public List<SysUser> listAll() {
        return this.list();
    }

    @Override
    public void addUser(UserDTO dto) {
        // 用户名查重
        LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(SysUser::getUsername, dto.getUsername());
        if (this.count(wrapper) > 0) {
            throw new RuntimeException("用户名已存在");
        }
        SysUser user = new SysUser();
        user.setUsername(dto.getUsername());
        // 密码加密
        user.setPassword(passwordEncoder.encode(dto.getPassword()));
        user.setRole(dto.getRole());
        this.save(user);
    }

    @Override
    public void updateUser(UserDTO dto) {
        SysUser user = this.getById(dto.getId());
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        // 改用户名则查重
        if (!user.getUsername().equals(dto.getUsername())) {
            LambdaQueryWrapper<SysUser> wrapper = new LambdaQueryWrapper<>();
            wrapper.eq(SysUser::getUsername, dto.getUsername());
            if (this.count(wrapper) > 0) {
                throw new RuntimeException("用户名已被占用");
            }
        }
        user.setUsername(dto.getUsername());
        user.setRole(dto.getRole());
        // 密码不为空才更新密码
        if (dto.getPassword() != null && !dto.getPassword().isEmpty()) {
            user.setPassword(passwordEncoder.encode(dto.getPassword()));
        }
        this.updateById(user);
    }
}