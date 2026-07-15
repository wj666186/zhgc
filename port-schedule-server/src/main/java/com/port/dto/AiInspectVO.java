package com.port.dto;

public class AiInspectVO {
    private String inspectNo;
    private String containerNo;
    private String damageResult;
    private String damageLevel;
    private Double confidence;
    private Long costMs;
    private String imageName;
    public String getImageName() {
        return imageName;
    }
    public void setImageName(String imageName) {
        this.imageName = imageName;
    }
    public String getInspectNo() {
        return inspectNo;
    }

    public void setInspectNo(String inspectNo) {
        this.inspectNo = inspectNo;
    }

    public String getContainerNo() {
        return containerNo;
    }

    public void setContainerNo(String containerNo) {
        this.containerNo = containerNo;
    }

    public String getDamageResult() {
        return damageResult;
    }

    public void setDamageResult(String damageResult) {
        this.damageResult = damageResult;
    }

    public String getDamageLevel() {
        return damageLevel;
    }

    public void setDamageLevel(String damageLevel) {
        this.damageLevel = damageLevel;
    }

    public Double getConfidence() {
        return confidence;
    }

    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }

    public Long getCostMs() {
        return costMs;
    }

    public void setCostMs(Long costMs) {
        this.costMs = costMs;
    }
}
