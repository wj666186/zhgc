package com.port.security;

import com.port.domain.entity.SysUser;
import lombok.Data;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import java.util.Collection;
import java.util.Collections;

@Data
public class LoginUser implements UserDetails {

    // 成员变量名称统一为 sysUser
    private SysUser sysUser;

    // 构造方法接收SysUser赋值
    public LoginUser(SysUser sysUser) {
        this.sysUser = sysUser;
    }

    // 实现账号密码
    @Override
    public String getUsername() {
        return sysUser.getUsername();
    }

    @Override
    public String getPassword() {
        return sysUser.getPassword();
    }

    // 直接对外获取角色
    public String getRole() {
        return sysUser.getRole();
    }

    // 权限空实现
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.emptyList();
    }

    @Override
    public boolean isAccountNonExpired() {
        return true;
    }
    @Override
    public boolean isAccountNonLocked() {
        return true;
    }
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }
    @Override
    public boolean isEnabled() {
        return true;
    }
}