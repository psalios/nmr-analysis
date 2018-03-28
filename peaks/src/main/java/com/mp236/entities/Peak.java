package com.mp236.entities;

import javax.persistence.*;

@Entity
@Table(name = "peaks")
public class Peak {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;

    @Column(name = "peak")
    private Double peak;

    @Column(name = "class")
    private String multiplicity;

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

    public String getMultiplicity() {
        return multiplicity;
    }

    public void setMultiplicity(String multiplicity) {
        this.multiplicity = multiplicity;
    }

    @Override
    public String toString() {
        return Double.toString(peak);
    }
}
