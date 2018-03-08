# Copyright (c) 2018 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '1.0.2'

import errno
import io
import os
import re
import subprocess
import sys


def convert(infile, outfile='README.rst', sanitize=True, encoding=None,
            check_manifest_in=True):
  """
  Uses Pandoc to convert the input file *infile* to reStructured Text and
  writes it to *outfile*. If *sanitize* is True, the output file will be
  sanitized for use on PyPI.

  Returns the content of the output file.
  """

  if check_manifest_in:
    if not os.path.isfile('MANIFEST.in'):
      raise RuntimeError('Missing MANIFEST.in. Create it and add REAMDE.rst to it.')
    else:
      with open('MANIFEST.in') as fp:
        found = False
        for line in fp:
          if re.match('include\s+README.rst', line):
            found = True
            break
        if not found:
          raise RuntimeError('You are missing README.rst in your MANIFEST.in file.')

  command = ['pandoc', '-s', infile, '-o', outfile]
  try:
    code = subprocess.call(command)
  except OSError as exc:
    if exc.errno != errno.ENOENT:
      raise
    # Pandoc command could not be found.
    print('Pandoc not found in PATH.')
    pandoc_bin = download_pandoc()
    command[0] = pandoc_bin
    code = subprocess.call(command)

  if code != 0:
    raise EnvironmentError('Pandoc returned non-zero exit code {!r}'
                           .format(code))

  if sanitize:
    sanitize_rest(outfile, encoding)

  with io.open(outfile, 'r', encoding=encoding) as fp:
    return fp.read()


def sanitize_rest(rstfile, encoding=None):
  """
  Sanitizes reStructured text in the file *rstfile* for use on PyPI. Currently,
  this is only about stripping `.. raw:: html` blocks from the file. The new
  contents will be written to the same *rstfile*.
  """

  with io.open('README.rst', encoding=encoding) as fp:
    text = fp.read()

  # Remove ".. raw:: html\n\n    ....\n" stuff, it results from using
  # raw HTML in Markdown but can not be properly rendered in PyPI.
  text = re.sub('..\s*raw::\s*html\s*\n\s*\n\s+[^\n]+\n', '', text, re.M)

  with io.open('README.rst', 'w', encoding=encoding) as fp:
    fp.write(text)


def download_pandoc():
  """
  Downloads Pandoc to the current user's `~/Downloads` directory and returns
  the path to it. The binary is downloaded from the Pandoc Github releases.
  Currently it will download Pandoc 2.1.2.
  """

  try:
    from urllib.request import urlopen
  except ImportError:
    from urllib2 import urlopen

  downloads_dir = os.path.expanduser('~/Downloads')
  try:
    os.makedirs(downloads_dir)
  except OSError as exc:
    if exc.errno != errno.EEXIST:
      raise

  if sys.platform.startswith('win32'):
    url = 'https://github.com/jgm/pandoc/releases/download/2.1.2/pandoc-2.1.2-windows.zip'
    extract_file = 'pandoc-2.1.2/pandoc.exe'
    filename = 'pandoc.exe'
    archive_driver = 'zip'
    from zipfile import ZipFile as open_archive
  elif sys.platform.startswith('darwin'):
    url = 'https://github.com/jgm/pandoc/releases/download/2.1.2/pandoc-2.1.2-macOS.zip'
    extract_file = 'pandoc-2.1.2/bin/pandoc'
    filename = 'pandoc'
    archive_driver = 'zip'
  elif sys.platform.startswith('linux'):
    url = 'https://github.com/jgm/pandoc/releases/download/2.1.2/pandoc-2.1.2-linux.tar.gz'
    extract_file = 'pandoc-2.1.2/bin/pandoc'
    filename = 'pandoc'
    archive_driver = 'tar.gz'
  else:
    raise EnvironmentError('unsupported platform: {!r}'.format(sys.platform))

  outfile = os.path.join(downloads_dir, filename)
  if os.path.isfile(outfile):
    print('Pandoc already in ~/Downloads.')
    return outfile

  if archive_driver == 'zip':
    import zipfile
    open_archive = lambda fp: zipfile.ZipFile(io.BytesIO(fp.read()))
  else:
    import tarfile
    open_archive = lambda fp: tarfile.open(fileobj=fp, mode='r|gz')

  import shutil
  import stat

  print('Downloading "{}" ...'.format(url))
  with urlopen(url) as urlfp:
    with open_archive(urlfp) as archive:
      with open(outfile, 'wb') as outfp:
        print('Extracting "{}" to "{}" ...'.format(extract_file, outfile))
        shutil.copyfileobj(archive.open(extract_file), outfp)
      st = os.stat(outfile)
      os.chmod(outfile, st.st_mode | stat.S_IEXEC)

  return outfile
