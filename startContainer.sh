#!/bin/sh
copyVersionFile() {
    cat /python-server.version > /version-store/python-server.version
}

copyVersionFile
cd /usr/local/python-server
python Spectrum.py