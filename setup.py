#! /usr/bin/env python
# -*- coding: utf-8 -*-


# e-story -- Open data based history lessons
# By: Anael Ichane <anael.ichane@gmail.com>
#     Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 Anael Ichane & Emmanuel Raviart
# http://github.com/aichane/e-story
#
# This file is part of e-story.
#
# e-story is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# e-story is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Open data based history lessons"""


try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


classifiers = """\
Development Status :: 2 - Pre-Alpha
Environment :: Web Environment
Intended Audience :: Information Technology
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: POSIX
Programming Language :: Python
Topic :: Scientific/Engineering :: Information Analysis
Topic :: Sociology
Topic :: Internet :: WWW/HTTP :: WSGI :: Server
"""

doc_lines = __doc__.split('\n')


setup(
    name = 'e-story',
    version = '0.1dev',

    author = 'Anael Ichane & Emmanuel Raviart',
    author_email = 'team@e-story.fr',
    classifiers = [classifier for classifier in classifiers.split('\n') if classifier],
    description = doc_lines[0],
    keywords = 'history lessons online opendata server web',
    license = 'http://www.fsf.org/licensing/licenses/agpl-3.0.html',
    long_description = '\n'.join(doc_lines[2:]),
    url = 'http://github.com/aichane/e-story',

    data_files = [
        ('share/locale/fr/LC_MESSAGES', ['estory/i18n/fr/LC_MESSAGES/e-story.mo']),
        ],
    entry_points = {
        'distutils.commands': 'build_assets = estory.commands:BuildAssets',
        'paste.app_factory': 'main = estory.application:make_app',
        },
    include_package_data = True,
    install_requires = [
        'Biryani1 >= 0.9dev',
        'bleach >= 1.2',
        'Mako >= 0.8',
        'Markdown >= 2.3',
        'PyYAML',
        'pymongo >= 2.2',
        'requests >= 1.2',
        'webassets >= 0.8',
        'WebError >= 0.10',
        'WebOb >= 1.1',
        ],
    message_extractors = {'estory': [
        ('**.py', 'python', None),
        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'}),
        ('static/**', 'ignore', None)]},
#    package_data = {'estory': ['i18n/*/LC_MESSAGES/*.mo']},
    packages = find_packages(),
    paster_plugins = ['PasteScript'],
    setup_requires = ['PasteScript >= 1.6.3'],
    zip_safe = False,
    )
