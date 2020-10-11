#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import os.path

def get_txt(filename):
    with open(filename) as txt_file:
        return txt_file.read()

readme = get_txt('README.rst') if os.path.isfile('README.rst') else ''
history = get_txt('HISTORY.rst') if os.path.isfile('HISTORY.rst') else ''

requirements = ['Click>=7.0', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="the prebid contributors",
    author_email='info@prebid.org',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Create and manage line items.",
    entry_points={
        'console_scripts': [
            'line_item_manager=line_item_manager.cli:main',
        ],
    },
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='line-item-manager',
    name='line-item-manager',
    packages=find_packages(include=['line_item_manager', 'line_item_manager.*']),
    package_dir={'line_item_manager': 'line_item_manager'},
    package_data={'line_item_manager': ['conf.d/*.yml']},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/prebid/line-item-manager',
    version='0.1.0',
    zip_safe=False,
)
