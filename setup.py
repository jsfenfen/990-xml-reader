from setuptools import setup
import os

NAME = 'irsx'
HUMAN_NAME = 'irsx'
HERE = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(HERE, 'irs_reader', '_version.py')) as f:
    exec(f.read(), {}, version_ns)

setup(name=HUMAN_NAME,
      description = "Turn the IRS' versioned XML 990's into python objects \
        with original line number and description.",
      version = version_ns['__version__'],
      author = 'Jacob Fenton',
      author_email = 'jsfenfen@gmail.com',
      url = 'https://github.com/jsfenfen/990-xml-reader',
      license = 'MIT',
      python_requires = '>=3.10',
      install_requires = ['requests', 'xmltodict'],
      tests_require = ['pytest'],
      packages = ['irsx'],
      package_dir = {'irsx': 'irs_reader'},
      package_data = {'irsx': ['metadata/*.csv']},
      keywords = ['990', 'nonprofit', 'tax'],
      entry_points = {
          "console_scripts": ["irsx=irsx.irsx_cli:main",
                              "irsx_index=irsx.irsx_index_cli:main",
                              "irsx_retrieve=irsx.irsx_retrieve_cli:main",
                              "irsx_bulk=irsx.irsx_bulk_cli:main"]
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
        ],
      )
