#! /usr/bin/env python
# -*- coding: utf-8 -*-


# e-story -- Open data based history lessons
# By: Anael Ichane <anael.ichane@gmail.com>
#     Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 Anael Ichane & Emmanuel Raviart
# http://github.com/etalab/e-story
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
import logging
import os
import re
import urllib2
import sys

from biryani1 import strings
import paste.deploy

from estory import contexts, conv, environment, model


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
temporal_coverage_re = re.compile(ur'(?P<from>19\d\d(\.(0\d|1[0-2])(\.([0-2]\d|3[0-1]))?)?)(\s*-\s*(?P<to>19\d\d(\.(0\d|1[0-2])(\.([0-2]\d|3[0-1]))?)?))?$')


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
    headers = {
        'User-Agent': 'e-story-bot/0.1 (https://www.github.com/aichane/e-story bot@e-story.co)',
        }
    request = urllib2.Request('http://www.data.gouv.fr/var/download/b903bf838d67642d31ac34bb46ea13ef.txt',
        headers = headers)
    response = urllib2.urlopen(request)
    labels = response.readline().decode('cp1252').strip().split(u'\t')
    for line in response:
        row = line.decode('cp1252').strip().split(u'\t')
        if not row:
            continue
        entry = conv.check(conv.struct(
            {
                u'REF': conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
#                u'NUMP',
#                u'PAYS',
#                u'REG',
#                u'DPT',
#                u'COM',
#                u'INSEE',
#                u'EDIF',
#                u'ADRESSE',
                u'LEG': conv.cleanup_line,
#                u'OBJ',
#                u'LIEUCOR',
#                u'AUTP',
#                u'AUTOEU',
#                u'SCLE',
                u'DATPV': conv.cleanup_text,
                u'SERIE': conv.cleanup_line,
#                u'TYPDOC',
#                u'LBASE',
                u'COPY': conv.pipe(
                    conv.cleanup_text,
                    conv.not_none,
                    ),
#                u'VIDEO-v',
                u'VIDEO-p': conv.pipe(
                    conv.make_input_to_url(full = True),
                    conv.not_none,
                    ),
                },
            default = conv.cleanup_line,
            ))(dict(zip(labels, row)), state = ctx)

        if entry[u'DATPV'] is None:
            continue
        temporal_coverage_match = temporal_coverage_re.match(entry[u'DATPV'])
        if temporal_coverage_match is None:
            log.warning(u'Invalid date: {}. Skipping {}'.format(entry[u'DATPV'], entry))
            continue
        temporal_coverage_from = temporal_coverage_match.group('from').replace(u'.', u'-')
        if temporal_coverage_match.group('to'):
            temporal_coverage_to = temporal_coverage_match.group('to').replace(u'.', u'-')
        else:
            temporal_coverage_to = None

        item = model.Item(
            image_url = entry[u'VIDEO-p'],
            rights = entry[u'COPY'],
            slug = strings.slugify(u'{}-{}'.format(entry[u'LEG'] or entry[u'SERIE'], entry[u'REF'])),
            tags = [u'guerre'],
            temporal_coverage_from = temporal_coverage_from,
            temporal_coverage_to = temporal_coverage_to,
            title = entry[u'LEG'] or entry[u'SERIE'] or entry[u'REF'],
            )
        item.save(ctx, safe = True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
