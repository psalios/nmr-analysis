package com.mp236.controllers;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
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

    private static final String COMPOUND_PATH = "/Users/mpsalios/Documents/sh/nmr-spectrum/nmr-spectrum/data/compounds/";
    private static final String COMPOUND_EXTENSION = ".svg";

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

        List<Spectrum> spectrums = new ArrayList<>();

        for (int i=0;i<shifts.length;i++) {
            List<Double> peaks = peakRepository.findInRange(shifts[i] - deviations[i], shifts[i] + deviations[i])
                    .stream()
                    .map(Peak::getPeak)
                    .collect(Collectors.toList());

            List<Spectrum> tmp = spectrumRepository.findInPeakList(peaks);

            if(i == 0) {
                spectrums.addAll(tmp);
            } else {
                spectrums.retainAll(tmp);
            }
        }

        List<String> compounds = spectrums.stream()
                .map(spectrum -> COMPOUND_PATH + spectrum.getSpectrum() + COMPOUND_EXTENSION)
                .filter(spectrum -> new File(spectrum).exists())
                .map(spectrum -> {
                    String compound = "";
                    try {
                        compound = String.join("", Files.readAllLines(Paths.get(spectrum), StandardCharsets.UTF_8));
                    } catch (IOException ignored) { }
                    return compound;
                }).collect(Collectors.toList());

        model.put("compounds", compounds);
        model.put("spectrums", spectrums);

//        Map<Spectrum, Integer> spectrumHash = new HashMap<>();
//        for(int i=0;i<shifts.length;i++) {
//            List<Double> peaks = peakRepository.findInRange(shifts[i] - deviations[i], shifts[i] + deviations[i])
//                    .stream()
//                    .map(Peak::getPeak)
//                    .collect(Collectors.toList());
//            List<Spectrum> spectrums = spectrumRepository.findInPeakList(peaks);
//
//            for(Spectrum s: spectrums) {
//                int times = 0;
//                if(spectrumHash.containsKey(s)) {
//                    times = spectrumHash.get(s);
//                }
//                spectrumHash.put(s, times + 1);
//            }
//        }
//
//        Map<Integer, List<Spectrum>> spectrumMap = new TreeMap<>((o1, o2) -> o2 - o1);
//        spectrumHash.forEach((spectrum, times) -> {
//            if(!spectrumMap.containsKey(times)) {
//                spectrumMap.put(times, new ArrayList<>());
//            }
//            spectrumMap.get(times).add(spectrum);
//        });
//
//        List<List<Spectrum>> spectrums = new ArrayList<>(spectrumMap.values());

        model.put("shifts", shifts);
        model.put("multiplicities", multiplicities);
        model.put("deviations", deviations);

        return "welcome";
    }

}
