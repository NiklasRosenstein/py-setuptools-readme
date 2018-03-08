## setuptools_readme

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert README files to reStructured Text with [Pandoc] and sanitize them for
PyPI. Supposed to be used inside your setup scripts.

```python
if any('dist' in x for x in sys.argv[1:]):
  import setuptools_readme
  setuptools_readme.convert('README.md', encoding='utf8')
# If you skip this check you need to make sure that the README.rst is
# included in the package in MANIFEST.in.
if os.path.isfile('README.rst'):  
  with io.open('README.rst', encoding='utf8') as fp:
    long_description = fp.read()
    del fp
else:
  long_description = ''
```

__Features__

* Automatically downloads Pandoc if it is not installed on your system
  (to ~/Downloads)
* Removes `.. raw:: html` blocks from the reST output file (as it breaks
  rendering on PyPI)

__To do__

Test automatic download step on Linux and macOS.

  [Pandoc]: http://www.pandoc.org/index.html

---

<p align="center">Copyright &copy; 2018 Niklas Rosenstein</p>
