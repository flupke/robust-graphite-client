#!/usr/bin/env python
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


setup_requires = []
if 'test' in sys.argv:
    setup_requires.append('pytest')
tests_requires = [
    'pytest',
    'pytest-cov>=1.8.1',
    'httmock',
    'mock',
]
dev_requires = [
    'sphinx',
]
install_requires = [
    'requests>=2.4.0',
]


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['robgracli']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='robust-graphite-client',
    version='0.0.4',
    license='MIT',
    author='Luper Rouch',
    author_email='luper.rouch@gmail.com',
    url='https://github.com/Stupeflix/robust-graphite-client',
    description='A simple graphite querying library with workarounds on some rare bugs',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={
        'tests': tests_requires,
        'dev': dev_requires,
    },
    tests_require=tests_requires,
    cmdclass={'test': PyTest},
    zip_safe=False,
    include_package_data=True,
)
