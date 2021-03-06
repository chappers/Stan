from setuptools import setup

MAJOR = 0
MINOR = 0
MICRO = 1
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)


setup(
    name             = 'stan',
    version          = VERSION,

    description      = 'Statistical Analysis System Transcompiler to Python',
    long_description = open("README.rst").read(),

    author           = 'Chapman Siu, David Qi, Matthew Seddon',
    author_email     = 'chapm0n.siu@gmail.com, linendave@hotmail.com, mattseddon@hotmail.com',
    url              = 'https://github.com/chappers/Stan/',
    license          = 'MIT License',

    packages         = ['stan', 'stan.data', 'stan.proc', 'stan.proc_functions', 'stan.transcompile'],

    classifiers      = [],

    install_requires = ['pyparsing', 'pandas', 'pandasql']
)

