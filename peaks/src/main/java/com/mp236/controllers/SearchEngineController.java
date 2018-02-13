package com.mp236.controllers;

import java.util.Map;

import com.mp236.entities.SpectrumRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class SearchEngineController {

    @Autowired
    private SpectrumRepository spectrumRepository;

    @RequestMapping("/")
    public String welcome(Map<String, Object> model) {

        model.put("spectrums", spectrumRepository.findAll());
        return "welcome";
    }

}
