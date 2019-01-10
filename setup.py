from setuptools import setup

setup(
    name='pymicruler',
    version='0.1.0',
    packages=['pymicruler', 'pymicruler.bp', 'pymicruler.utils'],
    package_data={'pymicruler': ['config/*.ini', 'resources/*', 'output/*']},
    url='http://ares-genetics.com',
    license='All rights reserved',
    author=['Victoria Beneder'],
    author_email='victoria.beneder@ares-genetics.com',
    description='',
    requires=['pandas', 'openpyxl', 'pyknow', 'xlrd', 'ete3', 'numpy'],
    install_requires=['pandas', 'openpyxl', 'pyknow', 'xlrd', 'ete3', 'numpy'],
    entry_points={
        'console_scripts': [
            'pymicruler=pymicruler.command_line:run'
        ]
    }
)