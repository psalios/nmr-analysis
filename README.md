# NMR Spectrum Viewer

## Installation
1. Create a virtual environment, a self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages. The module used to create and manage virtual environments is called [venv](https://docs.python.org/3/library/venv.html#module-venv).
```
virtualenv venv
```
2. Once you’ve created a virtual environment, you may activate it.

On Windows, run:
```
venv\Scripts\activate.bat
```
On Unix or MacOS, run:
```
source venv/bin/activate
```
3. Install all the necessary packages with `install -r`
```
pip install -r requirements.txt
```
4. Run the bokeh server
```
bokeh serve --show .
```
