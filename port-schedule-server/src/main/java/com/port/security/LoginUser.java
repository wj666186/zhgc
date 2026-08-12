package com.port.security;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.port.domain.entity.SysUser;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.io.Serializable;
import java.util.Collection;
import java.util.Collections;

@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class LoginUser implements UserDetails, Serializable {

    // 序列化版本号，固定防止反序列化版本冲突
    private static final long serialVersionUID = 1L;

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
    @JsonIgnore
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
