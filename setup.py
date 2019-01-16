# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='tcplite',
    version='0.0.1',
    description=(
        'a lite, flexible and extendable tcp framework'
    ),
    long_description=open('README.rst').read(),
    author='Vincent',
    author_email='wang.yuanqiu007@gmail.com',
    maintainer='Vincent',
    maintainer_email='wang.yuanqiu007@gmail.com',
    license='MIT License',
    packages=find_packages(),
    platforms=['all'],
    url='https://github.com/Vincent0700/tcplite.git',
    install_requires=[
        'attrs==18.2.0'
    ]
)
