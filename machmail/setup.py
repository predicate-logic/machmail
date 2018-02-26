from setuptools import setup
import sys
import os
from pip.req import parse_requirements

PACKAGE_DIR = {'': 'machmail'}
README = open("README.md").read()
LICENSE = open("LICENSE").read()
AUTHOR_EMAIL = 'mfwilson@gmail.com'

REQ = os.path.dirname(os.path.realpath(__file__))+"/requirements.txt"
install_reqs = parse_requirements(REQ, session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


def get_version(dir, package_name):
    """Get version string from package in non-module sub-dir.
    """
    path = './{}'.format(dir)
    sys.path.insert(0, path)
    version = __import__(package_name).__version__
    return version


# setup function
setup(name='machmail',
      # package metadata
      version=get_version(PACKAGE_DIR[''], 'machmail'),
      description=('Mail scraping utility.  Retrieve email attachements from '
                   'GMail and store locally'),
      long_description=README,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5.1',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='machinima gmail utility',
      url='http://github.com/predicatelogic/machmail',
      author='Mike Wilson',
      author_email=AUTHOR_EMAIL,
      license=LICENSE,

      # packages under package_dir
      packages=['machmail', 'machmail.util'],

      # Other libraries required by this library
      install_requires=[
        reqs
      ],

      # Install non-source files from MANIFEST.ini
      include_package_data=True,

      # Reduce size of package setup file by zipping it?
      zip_safe=False,

      # Define testing
      test_suite='nose.collector',
      tests_require=['nose>=1.0', 'nose-cover3'],

      # Make script callable from command-line using python module.
      # Preferred method of creating a script to call since it stays within
      # pyenv/virtualenv.
      entry_points={
           'console_scripts': ['machmail='
                               'machmail.cli:cli'],
      },
      )
