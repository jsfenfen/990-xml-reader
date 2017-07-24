from setuptools import setup


setup(name='990-xml-reader',
      version='0.1',
      packages=['990-xml-reader'],
      setup_requires=["wheel", "setuptools"],
      install_requires=["requests", "xmltodict"],
      tests_require=["nose",],
      )

