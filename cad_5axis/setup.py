import os
from setuptools import setup

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        f.read()

setup(
    name = "cad_5axis",
    version = "0.0.1",
    author = "Scott Martin",
    author_email = "smartin015@gmail.com",
    description = ("Tools and examples for generating machine code to cut objects on the PocketNC 5-axis CNC machine"),
    license = "BSD",
    keywords = "cnc cam cad cadquery 5axis",
    url = "http://packages.python.org/cad_5axis",
    packages=['ops', 'post', 'tools'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
