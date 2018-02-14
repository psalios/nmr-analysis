# NMR Spectrum Viewer

## Installation
1. Create a virtual environment, a self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages. The module used to create and manage virtual environments is called [venv](https://docs.python.org/3/library/venv.html#module-venv).
```bash
virtualenv venv
```
2. Once you’ve created a virtual environment, you may activate it.

On Unix or MacOS, run:
```bash
source venv/bin/activate
```
3. Install all the necessary packages with `install -r`.
```bash
pip install -r requirements.txt
```
If hashlib fails, use `easy_install` to install it and then rerun the installation command above.

4. Install MySQL Schema.
  * Create schema
  ```SQL
  CREATE SCHEMA {db};
  ```
  * Import schema
  ```SQL
  mysql -u {user} -p {db} < schema.sql
  ```
5. Run the bokeh server
```bash
bokeh serve --show .
```
