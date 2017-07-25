from setuptools import setup
import os


NAME = "irs_reader"
HERE = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(HERE, NAME, '_version.py')) as f:
    exec(f.read(), {}, version_ns)


setup(name=NAME,
      description="Turn the IRS' versioned XML 990's into python objects with original line number and description.",
      version=version_ns['__version__'],
      setup_requires=["setuptools",],
      install_requires=["requests", "xmltodict"],
      tests_require=["nose",],
      packages=["irs_reader"],
      package_dir={'irs_reader': 'irs_reader'},
      package_data={'irs_reader': ['data/*/*.json']},
      entry_points={
          "console_scripts": ["readxml=irs_reader.cli:main"]
      },
      )

