package com.port.mapper;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.port.domain.entity.Container;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import java.math.BigDecimal;

public interface ContainerMapper extends BaseMapper<Container> {

    /**
     * 装船：修改load_status = 1
     */
    @Update("UPDATE t_container SET load_status = 1 WHERE id = #{id}")
    int loadShip(@Param("id") Long id);

    /**
     * 卸船：修改load_status=0 + 所属区域
     */
    @Update("UPDATE t_container SET load_status = 0, area_no = #{areaNo} WHERE id = #{id}")
    int unLoadYard(@Param("id") Long id, @Param("areaNo") Integer areaNo);

    /**
     * 保存拖拽坐标：更新x z
     */
    @Update("UPDATE t_container SET x = #{x}, z = #{z} WHERE id = #{id}")
    int savePosition(
            @Param("id") Long id,
            @Param("x") BigDecimal x,
            @Param("z") BigDecimal z
    );

    // 新增：根据集装箱箱号查询单个箱体数据（补齐上层调用需要的方法）
    @Select("SELECT * FROM t_container WHERE container_no = #{boxNo}")
    Container selectByContainerNo(@Param("boxNo") String boxNo);
}
