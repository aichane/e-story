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


"""Controllers for tags"""


import itertools
import re

from .. import contexts, conv, model, urls, wsgihelpers


@wsgihelpers.wsgify
def api1_typeahead(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        q = params.get('q'),
        )
    data, errors = conv.struct(
        dict(
            q = conv.input_to_slug,
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Tag search error: {}').format(errors))

    tags = sorted(model.Item.get_collection().distinct('tags'))
    if data['q'] is not None:
        tag_re = re.compile(re.escape(data['q']))
        tags = (
            tag
            for tag in tags
            if tag is not None and tag_re.search(tag)
            )
    return wsgihelpers.respond_json(ctx,
        list(itertools.islice(tags, 10)),
        headers = headers,
        )


def route_api1_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/typeahead/?$', api1_typeahead),
        )
    return router(environ, start_response)
