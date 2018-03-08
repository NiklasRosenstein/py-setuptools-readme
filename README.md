## setuptools_readme

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Convert README files to reStructured Text with [Pandoc] and sanitize them for
PyPI. Supposed to be used inside your setup scripts.

```
# MANIFEST.in
include README.rst
include requirements.txt
```

```python
# setup.py
import io
import os
import setuptools

if any('dist' in x for x in sys.argv[1:]) and os.path.isfile('README.md'):
  try:
    import setuptools_readme
  except ImportError:
    print('Warning: README.rst could not be generated, setuptools_readme module missing.')
  else:
    setuptools_readme.convert('README.md', encoding='utf8')

with io.open('README.rst', encoding='utf8') as fp:
  long_description = fp.read()
```

__Features__

* Automatically downloads Pandoc if it is not installed on your system
  (to ~/Downloads)
* Removes `.. raw:: html` blocks from the reST output file (as it breaks
  rendering on PyPI)
* Errors if your `MANIFEST.in` does not contain the `include README.rst` line

__To do__

Test automatic download step on Linux and macOS.

  [Pandoc]: http://www.pandoc.org/index.html

---

<p align="center">Copyright &copy; 2018 Niklas Rosenstein</p>
