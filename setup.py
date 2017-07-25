from setuptools import setup

setup(name="irs_reader",
      version="0.1",
      setup_requires=["setuptools",],
      install_requires=["requests", "xmltodict"],
      tests_require=["nose",],
      packages=["irs_reader"],

      entry_points={
          "console_scripts": ["readxml=irs_reader.cli:main"]
      },
      )

