from setuptools import setup

def readme():
      with open("README.rst") as f:
            f.read()

setup(name='unicodeutil',
      version='0.1.dev0',
      description='Classes and functions for working with Unicode data.',
      long_description=readme(),
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
