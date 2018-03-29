CREATE TABLE `peaks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `peak` double(15,5) DEFAULT NULL,
  `class` varchar(3) NOT NULL DEFAULT 'm',
  `spectrum_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_peak_spectrum` (`peak`,`spectrum_id`),
  KEY `fk_peaks_spectrum` (`spectrum_id`),
  CONSTRAINT `fk_peaks_spectrum` FOREIGN KEY (`spectrum_id`) REFERENCES `spectrum` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25052 DEFAULT CHARSET=latin1;
