
import errno
import io
import os
import re
import subprocess
import sys


def convert(infile, outfile='README.rst', sanitize=True, encoding=None):
  """
  Uses Pandoc to convert the input file *infile* to reStructured Text and
  writes it to *outfile*. If *sanitize* is True, the output file will be
  sanitized for use on PyPI.
  """

  command = ['pandoc', '-s', infile, '-o', outfile]
  try:
    code = subprocess.call(command)
  except OSError as exc:
    if exc.errno != errno.ENOENT:
      raise
    # Pandoc command could not be found.
    print('Note: Pandoc could not be found. Downloading latest release ...',
          file=sys.stderr)
    pandoc_bin = download_pandoc()
    command[0] = pandoc_bin
    code = subprocess.call(command)

  if code != 0:
    raise EnvironmentError('Pandoc returned non-zero exit code {!r}'
                           .format(code))

  if sanitize:
    sanitize_rest(outfile, encoding)


def sanitize_rest(rstfile, encoding=None):
  """
  Sanitizes reStructured text in the file *rstfile* for use o PyPI. Currently,
  this is only about stripping `.. raw:: html` blocks from the file. The new
  contents will be written to the same *rstfile*/
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
