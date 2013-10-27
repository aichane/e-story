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


"""Download "Fonds de la guerre 14-18. Extrait de la base Mémoire" and add its content to items collection."""


import argparse
import csv
import logging
import os
import re
import sys

from biryani1 import strings
import paste.deploy

from estory import contexts, conv, environment, model


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
temporal_coverage_re = re.compile(ur'(?P<from>\d{3,4})(\s*-\s*(?P<to>\d{3,4}))?$')


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = "e-story configuration file")
    parser.add_argument('-s', '--section', default = 'main',
        help = "Name of configuration section in configuration file")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    site_conf = paste.deploy.appconfig('config:{0}#{1}'.format(os.path.abspath(args.config), args.section))
    environment.load_environment(site_conf.global_conf, site_conf.local_conf)

    ctx = contexts.null_ctx
    with open(os.path.join(os.path.dirname(__file__), 'grands-documents.csv')) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter = ',', quotechar = '"')
        labels = [
            label.decode('utf-8')
            for label in csv_reader.next()
            ]
        for row in csv_reader:
            if not row:
                continue
            row = [
                cell.decode('utf-8')
                for cell in row
                ]
            entry = conv.check(conv.struct(
                {
                    u'Titre du document': conv.pipe(
                        conv.cleanup_line,
                        conv.not_none,
                        ),
#                    u'Page',
#                    u'Institution',
                    u'Cote du document': conv.pipe(
                        conv.cleanup_line,
                        conv.not_none,
                        ),
#                    u'Cote origine',
                    u'Date du document': conv.cleanup_text,
#                    u'Support',
#                    u'Dimensions du document',
                    u'Source': conv.make_input_to_url(full = True),
                    },
                default = conv.cleanup_line,
                ))(dict(zip(labels, row)), state = ctx)

            if entry[u'Date du document'] is None or entry[u'Source'] is None:
                continue
            temporal_coverage_match = temporal_coverage_re.match(entry[u'Date du document'])
            if temporal_coverage_match is None:
                log.warning(u'Invalid date: {}. Skipping {}'.format(entry[u'Date du document'], entry))
                continue
            temporal_coverage_from = temporal_coverage_match.group('from').replace(u'.', u'-')
            if temporal_coverage_match.group('to'):
                temporal_coverage_to = temporal_coverage_match.group('to').replace(u'.', u'-')
            else:
                temporal_coverage_to = None

            item = model.Item(
                image_url = entry[u'Source'],
    #            rights = entry[u'COPY'],
                slug = strings.slugify(u'{}-{}'.format(entry[u'Titre du document'], entry[u'Cote du document'])),
                tags = [u'grand-document'],
                temporal_coverage_from = temporal_coverage_from,
                temporal_coverage_to = temporal_coverage_to,
                title = entry[u'Titre du document'],
                )
            item.save(ctx, safe = True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
