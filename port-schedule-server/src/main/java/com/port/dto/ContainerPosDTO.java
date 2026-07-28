package com.port.dto;

import lombok.Data;
import java.math.BigDecimal;

@Data
public class ContainerPosDTO {
    private Long id;
    private BigDecimal x;
    private BigDecimal z;
}
