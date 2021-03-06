
import io
import os
import setuptools
import setuptools_readme
import sys

if any('dist' in x for x in sys.argv):
  setuptools_readme.convert('README.md', encoding='utf8')
if os.path.isfile('README.rst'):
  with io.open('README.rst', encoding='utf8') as fp:
    long_description = fp.read()
    del fp
else:
  long_description = ''

setuptools.setup(
  name='setuptools-readme',
  version='1.0.2',
  license='MIT',
  url='https://github.com/NiklasRosenstein/py-setuptools-readme',
  author='Niklas Rosenstein',
  author_email='rosensteinniklas@gmail.com',
  description='Convert README files in setup scripts to reStructured Text with Pandoc for use on PyPI.',
  long_description=long_description,
  py_modules=['setuptools_readme']
)
