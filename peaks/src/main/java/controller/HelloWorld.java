package controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HelloWorld {

    @GetMapping("/")
    public String index(Model model) {

        model.addAttribute("message", "Hello Spring MVC 5!");
        return "index";
    }
}
