# NMR Spectrum search engine based on multiplet information

## Components

### [NMR Analysis Tool](https://github.com/psalios/sh/tree/master/nmr-spectrum)
The tool allows users to perform NMR Analysis on NMR spectra. It can perform peak picking on NMR spectra, chemical shift reference, determine integral intensity of peaks (i.e. area under the curve within certain limits) and produce multiplet reports.
The data are stored in the database in order to be used from the search engine (see below).

### [Search Engine on peaks and multiplet information](https://github.com/psalios/sh/tree/master/peaks)
The search engine allows users to determine chemical shifts (ppm), multiplicity and deviation (ppm) of carbon and proton spectrum. The search engine performs a whole or partial match search on the data stored in the database and returns the spectra that matches the input.
