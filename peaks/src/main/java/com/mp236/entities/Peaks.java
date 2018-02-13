package com.mp236.entities;

import javax.persistence.*;

@Entity
@Table(name = "peaks")
public class Peaks {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;

    @Column(name = "peak")
    private Double peak;

    @Column(name = "spectrum_id")
    private Integer spectrumId;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Double getPeak() {
        return peak;
    }

    public void setPeak(Double peak) {
        this.peak = peak;
    }

    public Integer getSpectrumId() {
        return spectrumId;
    }

    public void setSpectrumId(Integer spectrumId) {
        this.spectrumId = spectrumId;
    }

    @Override
    public String toString() {
        return Double.toString(peak);
    }
}
