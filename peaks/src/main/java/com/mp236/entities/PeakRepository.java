package com.mp236.entities;

import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface PeakRepository extends CrudRepository<Peak, Long>{

    @Query("SELECT p FROM Peak p WHERE (p.peak BETWEEN :start AND :stop) AND p.multiplicity LIKE :peak")
    List<Peak> findInRange(@Param("start") double start, @Param("stop") double stop, @Param("peak") String peak);
}
