# coding=utf-8

from setuptools import setup, find_packages

VERSION = '0.0.2'
PACKAGE_NAME = 'tcplite'

EXTRAS = {}
REQUIRES = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        if ';' in line:
            requirement, _, specifier = line.partition(';')
            for_specifier = EXTRAS.setdefault(':{}'.format(specifier), [])
            for_specifier.append(requirement)
        else:
            REQUIRES.append(line)

with open('test-requirements.txt') as f:
    TESTS_REQUIRES = f.readlines()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=(
        'a lite, flexible and extendable tcp framework'
    ),
    long_description=open('README.rst').read(),
    author='Vincent',
    author_email='wang.yuanqiu007@gmail.com',
    maintainer='Vincent',
    maintainer_email='wang.yuanqiu007@gmail.com',
    license='MIT License',
    packages=['tcplite'],
    platforms=['all'],
    url='https://github.com/Vincent0700/tcplite.git',
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRES,
    extras_require=EXTRAS,
)
