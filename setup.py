from setuptools import setup
import os


NAME = "xirsx"
HUMAN_NAME = 'xirsx'
HERE = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(HERE, 'irs_reader', '_version.py')) as f:
    exec(f.read(), {}, version_ns)


setup(name=HUMAN_NAME,
      description="Turn the IRS' versioned XML 990's into python objects with original line number and description.",
      version=version_ns['__version__'],
      setup_requires=["setuptools",],
      install_requires=["requests", "xmltodict"],
      tests_require=["nose",],
      packages=["xirsx"],
      package_dir={'xirsx': 'irs_reader'},
      package_data={'xirsx': ['data/*/*.json']},
      entry_points={
          "console_scripts": ["xirsx=xirsx.cli:main", "xirsx_index=xirsx.cli_index:main"]
      },
      )

