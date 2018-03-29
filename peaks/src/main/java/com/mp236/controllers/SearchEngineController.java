package com.mp236.controllers;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import com.mp236.Compound;
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

    private static final String COMPOUND_PATH = "/Users/mpsalios/Documents/sh/nmr-spectrum/data/compounds/";
    private static final String COMPOUND_EXTENSION = ".svg";

    @Autowired
    private SpectrumRepository spectrumRepository;

    @Autowired
    private PeakRepository peakRepository;

    @RequestMapping("/")
    public String welcome(
            @RequestParam(value = "shift[]", defaultValue = "") ArrayList<Double> shifts,
            @RequestParam(value = "multiplicity[]", defaultValue = "") ArrayList<String> multiplicities,
            @RequestParam(value = "deviation[]", defaultValue = "") ArrayList<Double> deviations,
            @RequestParam(value = "style", defaultValue = "old") String style,
            Map<String, Object> model
    ) {

        List<Spectrum> spectrums = new ArrayList<>();

        for (int i=0;i<shifts.size();i++) {
            double start = shifts.get(i) - deviations.get(i);
            double stop = shifts.get(i) + deviations.get(i);

            String multiplicity = multiplicities.get(i).equals("any") ? "%" : multiplicities.get(i);
            List<Double> peaks = peakRepository.findInRange(start, stop, multiplicity)
                    .stream()
                    .map(Peak::getPeak)
                    .collect(Collectors.toList());

            if (!peaks.isEmpty()) {
                List<Spectrum> tmp = spectrumRepository.findInPeakList(peaks);

                if(i == 0) {
                    spectrums.addAll(tmp);
                } else {
                    spectrums.retainAll(tmp);
                }
            } else {
                spectrums.clear();
                break;
            }
        }

        List<Compound> compounds = getCompounds(spectrums);

        String query = paramsQuery(shifts, multiplicities, deviations);

        model.put("compounds", compounds);

        model.put("shifts", shifts);
        model.put("multiplicities", multiplicities);
        model.put("deviations", deviations);
        model.put("style", style);
        model.put("query", query);

        return "welcome";
    }

    List<Compound> getCompounds(List<Spectrum> spectrums) {
        return spectrums.stream()
                .map(spectrum -> {
                    String path = COMPOUND_PATH + spectrum.getSpectrum() + COMPOUND_EXTENSION;

                    String image = "";
                    if (new File(path).exists()) {
                        try {
                            image = String.join("", Files.readAllLines(Paths.get(path), StandardCharsets.UTF_8));
                        } catch (IOException ignored) { }
                    }
                    return new Compound(spectrum.getSpectrum(), image);
                }).collect(Collectors.toList());
    }

    String paramsQuery(List<Double> shifts, List<String> multiplicities, List<Double> deviations) {
        StringJoiner stringJoiner = new StringJoiner("&");
        IntStream.range(0, shifts.size())
                .forEach(i -> stringJoiner
                        .add("shift%5B%5D="+shifts.get(i))
                        .add("multiplicity%5B%5D="+multiplicities.get(i))
                        .add("deviation%5B%5D="+deviations.get(i)));
        return stringJoiner.toString();
    }

}
