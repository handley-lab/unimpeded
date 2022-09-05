#!/usr/bin/env python3
from setuptools import setup, find_packages


def readme(short=False):
    with open('README.rst') as f:
        if short:
            return f.readlines()[1].strip()
        else:
            return f.read()


def get_version(short=False):
    with open('README.rst') as f:
        for line in f:
            if ':Version:' in line:
                ver = line.split(':')[2].strip()
                if short:
                    subver = ver.split('.')
                    return '%s.%s' % tuple(subver[:2])
                else:
                    return ver


setup(name='unimpeded',
      version=get_version(),
      description=readme(short=True),
      long_description=readme(),
      author='Will Handley',
      author_email='wh260@cam.ac.uk',
      url='https://github.com/handley-lab/unimpeded',
      packages=find_packages(),
      scripts=[],
      install_requires=open('requirements.txt').read().splitlines(),
      setup_requires=['pytest-runner'],
      extras_require={
          'docs': ['sphinx', 'sphinx_rtd_theme', 'numpydoc'],
          },
      tests_require=['pytest', 'packaging'],
      include_package_data=True,
      license='MIT',
      classifiers=[
                   'Development Status :: 1 - Planning',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'Natural Language :: English',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6',
                   'Programming Language :: Python :: 3.7',
                   'Programming Language :: Python :: 3.8',
                   'Programming Language :: Python :: 3.9',
                   'Programming Language :: Python :: 3.10',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Astronomy',
                   'Topic :: Scientific/Engineering :: Physics',
                   'Topic :: Scientific/Engineering :: Visualization',
                   'Topic :: Scientific/Engineering :: Information Analysis',
                   'Topic :: Scientific/Engineering :: Mathematics',
      ],
      )
