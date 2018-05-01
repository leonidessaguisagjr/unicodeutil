from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='unicodeutil',
      version='0.1.dev3',
      description='Classes and functions for working with Unicode data.',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Topic :: Software Development :: Internationalization",
            "Topic :: Software Development :: Libraries",
            "Topic :: Text Processing",
            "Topic :: Text Processing :: Linguistic",
      ],
      url='https://github.com/leonidessaguisagjr/unicodeutil',
      author='Leonides T. Saguisag Jr.',
      author_email='leonidessaguisagjr@gmail.com',
      license='MIT',
      packages=['unicodeutil'],
      install_requires=[
            'six',
      ],
      include_package_data=True,
      zip_safe=False)
