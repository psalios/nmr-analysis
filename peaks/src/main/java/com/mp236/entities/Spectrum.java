package com.mp236.entities;

import com.google.common.base.Joiner;

import javax.persistence.*;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "spectrum")
public class Spectrum {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Integer id;

    @OneToMany
    @JoinColumn(name = "spectrum_id")
    private Set<Peaks> peaks = new HashSet<>();

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getPeaks() {
        return Joiner.on(" ").skipNulls().join(peaks);
    }

    public void setPeaks(Set<Peaks> peaks) {
        this.peaks = peaks;
    }
}
