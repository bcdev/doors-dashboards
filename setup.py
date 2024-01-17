# The MIT License (MIT)
# Copyright (c) 2024 by Brockmann Consult
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from setuptools import setup, find_packages

requirements = [
    # requirements are given in file ./environment.yml.
]

packages = find_packages(exclude=["test", "test.*"])

# Same effect as "from doors_dashboards import __version__",
# but avoids importing doors_dashboards:
__version__ = None
with open('doors_dashboards/version.py') as f:
    exec(f.read())

# noinspection PyTypeChecker
setup(
    name="doors-dashboards",
    version=__version__,
    description=(
        'A package to create dashboard in context of the DOORS project'
    ),
    license='MIT',
    author='Ruchi Motwani (Brockmann Consult GmbH), '
           'Tonio Fincke (Brockmann Consult GmbH)',
    packages=packages,
    install_requires=requirements,
)