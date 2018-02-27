package com.mp236.controllers;

import java.util.*;
import java.util.stream.Collectors;

import com.mp236.entities.Peak;
import com.mp236.entities.PeakRepository;
import com.mp236.entities.Spectrum;
import com.mp236.entities.SpectrumRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class SearchEngineController {

    @Autowired
    private SpectrumRepository spectrumRepository;

    @Autowired
    private PeakRepository peakRepository;

    @RequestMapping("/")
    public String welcome(
            @RequestParam(value = "shift[]", defaultValue = "") double[] shifts,
            @RequestParam(value = "multiplicity[]", defaultValue = "") String[] multiplicities,
            @RequestParam(value = "deviation[]", defaultValue = "") double[] deviations,
            Map<String, Object> model
    ) {

        Map<Spectrum, Integer> spectrumHash = new HashMap<>();
        for(int i=0;i<shifts.length;i++) {
            List<Double> peaks = peakRepository.findInRange(shifts[i] - deviations[i], shifts[i] + deviations[i])
                    .stream()
                    .map(Peak::getPeak)
                    .collect(Collectors.toList());
            List<Spectrum> spectrums = spectrumRepository.findInPeakList(peaks);

            for(Spectrum s: spectrums) {
                int times = 0;
                if(spectrumHash.containsKey(s)) {
                    times = spectrumHash.get(s);
                }
                spectrumHash.put(s, times + 1);
            }
        }

        Map<Integer, List<Spectrum>> spectrumMap = new TreeMap<>((o1, o2) -> o2 - o1);
        spectrumHash.forEach((spectrum, times) -> {
            if(!spectrumMap.containsKey(times)) {
                spectrumMap.put(times, new ArrayList<>());
            }
            spectrumMap.get(times).add(spectrum);
        });

        List<List<Spectrum>> spectrums = new ArrayList<>();
        spectrumMap.values().forEach(spectrums::add);
        model.put("spectrums", spectrums);

        model.put("shifts", shifts);
        model.put("multiplicities", multiplicities);
        model.put("deviations", deviations);

        return "welcome";
    }

}
