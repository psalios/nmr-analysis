package com.mp236.entities;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface SpectrumRepository extends CrudRepository<Spectrum, Long> {

    @Query("SELECT DISTINCT s FROM Spectrum s JOIN s.peaks p WHERE p.peak IN :peaks ORDER BY s.date DESC")
    List<Spectrum> findInPeakList(@Param("peaks") List<Double> peaks);

}
