package com.mp236.entities;

import com.google.common.base.Joiner;

import javax.persistence.*;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

@Entity
@Table(name = "spectrum")
public class Spectrum {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;

    @OneToMany
    @JoinColumn(name = "spectrum_id")
    private List<Peak> peaks = new ArrayList<>();

    @Column(name = "spectrum")
    private Integer spectrum;

    @Column(name = "date")
    private Date date;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getPeaks() {
        return Joiner.on(" ").skipNulls().join(peaks);
    }

    public void setPeaks(ArrayList<Peak> peaks) {
        this.peaks = peaks;
    }

    public Date getDate() {
        return date;
    }

    public void setDate(Date date) {
        this.date = date;
    }

    public Integer getSpectrum() {
        return spectrum;
    }

    public void setSpectrum(Integer spectrum) {
        this.spectrum = spectrum;
    }
}
