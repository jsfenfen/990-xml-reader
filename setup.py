from setuptools import setup
import os


NAME = "irsx"
HUMAN_NAME = 'irsx'
HERE = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(HERE, 'irs_reader', '_version.py')) as f:
    exec(f.read(), {}, version_ns)


setup(name=HUMAN_NAME,
      description="Turn the IRS' versioned XML 990's into python objects with original line number and description.",
      version=version_ns['__version__'],
      setup_requires=["setuptools",],
      install_requires=["requests", "xmltodict", "unicodecsv"],
      tests_require=["nose",],
      packages=["irsx"],
      package_dir={'irsx': 'irs_reader'},
      package_data={'irsx': ['data/*/*.json']},
      entry_points={
          "console_scripts": ["irsx=irsx.irsx_cli:main", "irsx_index=irsx.irsx_cli_index:main"]
      },
      )

