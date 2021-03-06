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


"""Controllers for items"""


import collections
import datetime
import logging
import re

import pymongo
import webob
import webob.multidict

from .. import contexts, conv, model, paginations, templates, urls, wsgihelpers


inputs_to_item_data = conv.struct(
    dict(
        content = conv.cleanup_text,
        description = conv.cleanup_text,
        image_url = conv.make_input_to_url(full = True),
        rights = conv.cleanup_text,
        tag = conv.pipe(
            conv.uniform_sequence(
                conv.input_to_slug,
                drop_none_items = True,
                ),
            conv.empty_to_none,
            ),
        temporal_coverage_from = conv.pipe(
            conv.input_to_year_or_month_or_day_str,
            conv.not_none,
            ),
        temporal_coverage_to = conv.input_to_year_or_month_or_day_str,
        territorial_coverage = conv.pipe(
            conv.uniform_sequence(
#                conv.input_to_territory,
                conv.cleanup_line,  # TODO
                drop_none_items = True,
                ),
            conv.empty_to_none,
            ),
        title = conv.pipe(
            conv.cleanup_line,
            conv.not_none,
            ),
        url = conv.make_input_to_url(full = True),
        ),
    default = 'drop',
    )
log = logging.getLogger(__name__)


@wsgihelpers.wsgify
def admin_delete(req):
    ctx = contexts.Ctx(req)
    item = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Deletion unauthorized"),
            message = ctx._("You can not delete an item."),
            title = ctx._('Operation denied'),
            )
    if user._id != item.user_id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete an item."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        item.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.Item.get_admin_class_url(ctx))
    return templates.render(ctx, '/items/admin-delete.mako', item = item)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    item = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Edition unauthorized"),
            message = ctx._("You can not edit an item."),
            title = ctx._('Operation denied'),
            )
    if user._id != item.user_id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit an item."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            content = item.content,
            description = item.description,
            image_url = item.image_url,
            rights = item.rights,
            tag = item.tags,
            temporal_coverage_from = item.temporal_coverage_from,
            temporal_coverage_to = item.temporal_coverage_to,
            territorial_coverage = item.territorial_coverage,
            title = item.title,
            url = item.url,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_item_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_item_data(inputs, state = ctx)
        if errors is None:
            data['slug'], error = conv.pipe(
                conv.input_to_slug,
                conv.not_none,
                )(data['title'], state = ctx)
            if error is not None:
                errors = dict(title = error)
        if errors is None:
            if model.Item.find(
                    dict(
                        _id = {'$ne': item._id},
                        slug = data['slug'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(full_name = ctx._('An item with the same name already exists.'))
        if errors is None:
            data['tags'] = data.pop('tag')
            item.set_attributes(**data)
            if item.user_id is None or not user.admin:
                item.user_id = user._id
            item.save(ctx, safe = True)

            # View item.
            return wsgihelpers.redirect(ctx, location = item.get_admin_url(ctx))
    return templates.render(ctx, '/items/admin-edit.mako', item = item, errors = errors, inputs = inputs)


@wsgihelpers.wsgify
def admin_index(req):
    ctx = contexts.Ctx(req)
#    model.is_admin(ctx, check = True)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        advanced_search = params.get('advanced_search'),
        page = params.get('page'),
        sort = params.get('sort'),
        tag = params.get('tag'),
        term = params.get('term'),
        user = params.get('user'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                advanced_search = conv.guess_bool,
                page = conv.pipe(
                    conv.input_to_int,
                    conv.test_greater_or_equal(1),
                    conv.default(1),
                    ),
                sort = conv.pipe(
                    conv.cleanup_line,
                    conv.test_in(['slug', 'temporal_coverage_from', 'timestamp']),
                    ),
                tag = conv.input_to_slug,
                term = conv.input_to_slug,
                user = conv.pipe(
                    conv.input_to_slug,
                    model.Account.make_id_or_slug_to_instance(),
                    ),
                ),
            ),
        conv.rename_item('page', 'page_number'),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Item search error: {}').format(errors))

    criteria = {}
    if data['tag'] is not None:
        criteria['tags'] = re.compile(re.escape(data['tag']))
    if data['term'] is not None:
        criteria['slug'] = re.compile(re.escape(data['term']))
    if data['user'] is not None:
        criteria['user_id'] = data['user']._id
    cursor = model.Item.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'slug':
        cursor.sort([('slug', pymongo.ASCENDING)])
    elif data['sort'] == 'temporal_coverage_from':
        cursor.sort([(data['sort'], pymongo.ASCENDING), ('slug', pymongo.ASCENDING)])
    elif data['sort'] == 'timestamp':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('slug', pymongo.ASCENDING)])
    items = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/items/admin-index.mako', data = data, items = items, errors = errors,
        inputs = inputs, pager = pager)


@wsgihelpers.wsgify
def admin_new(req):
    ctx = contexts.Ctx(req)

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Creation unauthorized"),
            message = ctx._("You can not create an item."),
            title = ctx._('Operation denied'),
            )

    item = model.Item()
    if req.method == 'GET':
        errors = None
        inputs = extract_item_inputs_from_params(ctx)
    else:
        assert req.method == 'POST'
        inputs = extract_item_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_item_data(inputs, state = ctx)
        if errors is None:
            data['slug'], error = conv.pipe(
                conv.input_to_slug,
                conv.not_none,
                )(data['title'], state = ctx)
            if error is not None:
                errors = dict(title = error)
        if errors is None:
            if model.Item.find(
                    dict(
                        slug = data['slug'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(full_name = ctx._('An item with the same name already exists.'))
        if errors is None:
            data['tags'] = data.pop('tag')
            item.set_attributes(**data)
            item.user_id = user._id
            item.save(ctx, safe = True)

            # View item.
            return wsgihelpers.redirect(ctx, location = item.get_admin_url(ctx))
    return templates.render(ctx, '/items/admin-new.mako', errors = errors, inputs = inputs, item = item)


@wsgihelpers.wsgify
def admin_toggle_lesson(req):
    ctx = contexts.Ctx(req)
    item = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Lesson toggle unauthorized"),
            message = ctx._("You can not toggle a item in a lesson."),
            title = ctx._('Operation denied'),
            )

    session = ctx.session
    lesson = session.get_lesson(ctx)
    if lesson is None:
        return wsgihelpers.not_found(ctx,
            explanation = ctx._("No current lesson"),
            message = ctx._("There is no current lesson."),
            title = ctx._('Operation denied'),
            )
    if user._id != lesson.user_id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Lesson toggle forbidden"),
            message = ctx._("You can not toggle an item in a lesson."),
            title = ctx._('Operation denied'),
            )

    if lesson.items_id is None:
        lesson.items_id = []
    if item._id in lesson.items_id:
        lesson.items_id.remove(item._id)
        if not lesson.items_id:
            del lesson.items_id
    else:
        lesson.items_id.append(item._id)
    lesson.save(ctx, safe = True)

    # View lesson.
    return wsgihelpers.redirect(ctx, location = lesson.get_admin_url(ctx))


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    item = ctx.node

#    model.is_admin(ctx, check = True)

    return templates.render(ctx, '/items/admin-view.mako', item = item)


@wsgihelpers.wsgify
def api1_delete(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'DELETE', req.method

    content_type = req.content_type
    if content_type is not None:
        content_type = content_type.split(';', 1)[0].strip()
    if content_type == 'application/json':
        inputs, error = conv.pipe(
            conv.make_input_to_json(),
            conv.test_isinstance(dict),
            )(req.body, state = ctx)
        if error is not None:
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = 400,  # Bad Request
                        errors = [error],
                        message = ctx._(u'Invalid JSON in request DELETE body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                headers = headers,
                )
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)

    data, errors = conv.struct(
        dict(
            # Shared secret between client and server
            api_key = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_token,
                conv.not_none,
                ),
            # For asynchronous calls
            context = conv.test_isinstance(basestring),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = inputs.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [errors],
                    message = ctx._(u'Bad parameters in request'),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    api_key = data['api_key']
    account = model.Account.find_one(
        dict(
            api_key = api_key,
            ),
        as_class = collections.OrderedDict,
        )
    if account is None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 401,  # Unauthorized
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )
    if not account.admin:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 403,  # Forbidden
                    message = ctx._('Non-admin API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    item = ctx.node
    deleted_value = conv.check(conv.method('turn_to_json'))(item, state = ctx)
    item.delete(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = deleted_value,
            ).iteritems())),
        headers = headers,
        )


@wsgihelpers.wsgify
def api1_delete_related(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'DELETE', req.method

    content_type = req.content_type
    if content_type is not None:
        content_type = content_type.split(';', 1)[0].strip()
    if content_type == 'application/json':
        inputs, error = conv.pipe(
            conv.make_input_to_json(),
            conv.test_isinstance(dict),
            )(req.body, state = ctx)
        if error is not None:
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = 400,  # Bad Request
                        errors = [error],
                        message = ctx._(u'Invalid JSON in request DELETE body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                headers = headers,
                )
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)

    data, errors = conv.struct(
        dict(
            # Shared secret between client and server
            api_key = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_token,
                conv.not_none,
                ),
            # For asynchronous calls
            context = conv.test_isinstance(basestring),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = inputs.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [errors],
                    message = ctx._(u'Bad parameters in request'),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    api_key = data['api_key']
    account = model.Account.find_one(
        dict(
            api_key = api_key,
            ),
        as_class = collections.OrderedDict,
        )
    if account is None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 401,  # Unauthorized
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )
    if not account.admin:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 403,  # Forbidden
                    message = ctx._('Non-admin API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    related_id, error = conv.pipe(
        conv.input_to_token,
        conv.not_none,
        )(req.urlvars.get('id'), state = ctx)
    if error is None:
        item = model.Item.find_one({'related.id': related_id}, as_class = collections.OrderedDict)
        if item is None:
            error = ctx._(u'No item containing a related link with ID {0}').format(related_id)
        else:
            for related_index, related_link in enumerate(item.related or []):
                if related_id == related_link['id']:
                    del item.related[related_index]
                    if not item.related:
                        del item.related
                    break
            else:
                error = ctx._(u'No related link with ID {0}').format(related_id)
    if error is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Related Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    item.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = related_link,
            ).iteritems())),
        headers = headers,
        )


@wsgihelpers.wsgify
def api1_get(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET', req.method
    params = req.GET
    inputs = dict(
        callback = params.get('callback'),
        context = params.get('context'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                callback = conv.pipe(
                    conv.test_isinstance(basestring),
                    conv.cleanup_line,
                    ),
                context = conv.test_isinstance(basestring),
                ),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            dict(
                apiVersion = '1.0',
                context = inputs['context'],
                error = dict(
                    code = 400,  # Bad Request
                    errors = [
                        dict(
                            location = key,
                            message = error,
                            )
                        for key, error in sorted(errors.iteritems())
                        ],
                    # message will be automatically defined.
                    ),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ),
            headers = headers,
            jsonp = inputs['callback'],
            )

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(ctx.node, state = ctx),
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


@wsgihelpers.wsgify
def api1_index(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method in ('GET', 'POST'), req.method

    inputs_converters = dict(
        callback = conv.pipe(
            conv.test_isinstance(basestring),
            conv.cleanup_line,
            ),
        context = conv.test_isinstance(basestring),
        format = conv.pipe(
            conv.test_isinstance(basestring),
            conv.input_to_slug,
            conv.test_in([
#                'atom',
#                'json',
                ]),  # When None, return only the IDs of the items.
            ),
        page = conv.pipe(
            conv.anything_to_int,
            conv.test_greater_or_equal(1),
            # conv.default(1),  # Set below.
            ),
        sort = conv.pipe(
            conv.test_isinstance(basestring),
            conv.cleanup_line,
            conv.test_in(['slug', 'timestamp']),
            ),
        tag = conv.pipe(
            conv.test_isinstance(basestring),
            conv.input_to_slug,
            ),
        term = conv.pipe(
            conv.test_isinstance(basestring),
            conv.cleanup_line,
            ),
        )

    content_type = req.content_type
    if content_type is not None:
        content_type = content_type.split(';', 1)[0].strip()
    if content_type == 'application/json':
        inputs, error = conv.pipe(
            conv.make_input_to_json(),
            conv.test_isinstance(dict),
            )(req.body, state = ctx)
        if error is not None:
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = 400,  # Bad Request
                        errors = [error],
                        message = ctx._(u'Invalid JSON in request POST body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                headers = headers,
                )
    else:
        # URL-encoded GET or POST.
        inputs = dict(req.params)

    data, errors = conv.struct(inputs_converters)(inputs, state = ctx)
    if errors is None:
        if data['format'] is None:
            # Return full list of item ids, ignoring page number and sort criteria.
            data, errors = conv.struct(
                dict(
                    page = conv.test_none(),
                    sort = conv.test_none(),
                    target = conv.test_none(),
                    ),
                default = conv.noop,
                )(data, state = ctx)
        elif data['format'] == 'atom':
            # Always use timestamp as sort criteria for Atom format.
            data, errors = conv.struct(
                dict(
                    page = conv.default(1),
                    sort = conv.pipe(
                        conv.test_none(),
                        conv.default(u'timestamp'),
                        ),
                    ),
                default = conv.noop,
                )(data, state = ctx)
        else:
            assert data['format'] == 'json'
            data, errors = conv.struct(
                dict(
                    page = conv.default(1),
                    target = conv.test_none(),
                    ),
                default = conv.noop,
                )(data, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            dict(
                apiVersion = '1.0',
                context = inputs.get('context'),
                error = dict(
                    code = 400,  # Bad Request
                    errors = [
                        dict(
                            location = key,
                            message = error,
                            )
                        for key, error in sorted(errors.iteritems())
                        ],
                    # message will be automatically defined.
                    ),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ),
            headers = headers,
            jsonp = inputs.get('callback'),
            )
    data['page_number'] = data.pop('page')

    criteria = {}
    if data['tag'] is not None:
        criteria['tags'] = re.compile(re.escape(data['tag']))
    if data['term'] is not None:
        criteria['slug'] = re.compile(re.escape(data['term']))

    if data['format'] is None:
        # Return full list of item ids, ignoring page number and sort criteria.
        cursor = model.Item.get_collection().find(criteria, [])
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                value = [
                    item_attributes['_id']
                    for item_attributes in cursor
                    ],
                ).iteritems())),
            headers = headers,
            jsonp = data['callback'],
            )
    cursor = model.Item.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'slug':
        cursor.sort([('slug', pymongo.ASCENDING)])
    elif data['sort'] == 'timestamp':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('slug', pymongo.ASCENDING)])
    cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    if data['format'] == 'atom':
        return templates.render(ctx, '/items/atom.mako', cursor = cursor, data = data, inputs = inputs,
            pager = pager)
    assert data['format'] == 'json'
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = [
                conv.check(conv.method('turn_to_json'))(item, state = ctx)
                for item in cursor
                ],
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


#@wsgihelpers.wsgify
#def api1_set(req):
#    ctx = contexts.Ctx(req)
#    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

#    assert req.method == 'POST', req.method

#    inputs_converters = dict(
#        # Shared secret between client and server
#        api_key = conv.pipe(
#            conv.test_isinstance(basestring),
#            conv.input_to_token,
#            conv.not_none,
#            ),
#        # For asynchronous calls
#        context = conv.test_isinstance(basestring),
#        )

#    content_type = req.content_type
#    if content_type is not None:
#        content_type = content_type.split(';', 1)[0].strip()
#    if content_type == 'application/json':
#        inputs, error = conv.pipe(
#            conv.make_input_to_json(),
#            conv.test_isinstance(dict),
#            )(req.body, state = ctx)
#        if error is not None:
#            return wsgihelpers.respond_json(ctx,
#                collections.OrderedDict(sorted(dict(
#                    apiVersion = '1.0',
#                    error = collections.OrderedDict(sorted(dict(
#                        code = 400,  # Bad Request
#                        errors = [error],
#                        message = ctx._(u'Invalid JSON in request POST body'),
#                        ).iteritems())),
#                    method = req.script_name,
#                    params = req.body,
#                    url = req.url.decode('utf-8'),
#                    ).iteritems())),
#                headers = headers,
#                )
#        inputs_converters.update(dict(
#            value = conv.pipe(
#                conv.json_to_item_attributes,
#                conv.not_none,
#                ),
#            ))
#    else:
#        # URL-encoded POST.
#        inputs = dict(req.POST)
#        inputs_converters.update(dict(
#            value = conv.pipe(
#                conv.make_input_to_json(),
#                conv.json_to_item_attributes,
#                conv.not_none,
#                ),
#            ))

#    data, errors = conv.struct(inputs_converters)(inputs, state = ctx)
#    if errors is not None:
#        return wsgihelpers.respond_json(ctx,
#            collections.OrderedDict(sorted(dict(
#                apiVersion = '1.0',
#                context = inputs.get('context'),
#                error = collections.OrderedDict(sorted(dict(
#                    code = 400,  # Bad Request
#                    errors = [errors],
#                    message = ctx._(u'Bad parameters in request'),
#                    ).iteritems())),
#                method = req.script_name,
#                params = inputs,
#                url = req.url.decode('utf-8'),
#                ).iteritems())),
#            headers = headers,
#            )

#    api_key = data['api_key']
#    account = model.Account.find_one(
#        dict(
#            api_key = api_key,
#            ),
#        as_class = collections.OrderedDict,
#        )
#    if account is None:
#        return wsgihelpers.respond_json(ctx,
#            collections.OrderedDict(sorted(dict(
#                apiVersion = '1.0',
#                context = data['context'],
#                error = collections.OrderedDict(sorted(dict(
#                    code = 401,  # Unauthorized
#                    message = ctx._('Unknown API Key: {}').format(api_key),
#                    ).iteritems())),
#                method = req.script_name,
#                params = inputs,
#                url = req.url.decode('utf-8'),
#                ).iteritems())),
#            headers = headers,
#            )
#    # TODO: Handle account rights.

#    item_attributes = data['value']
#    item = model.Item.find_one(item_attributes['_id'], as_class = collections.OrderedDict)
#    if item is not None and item.draft_id != item_attributes.get('draft_id'):
#        # The modified item is not based on the latest version of the item.
#        return wsgihelpers.respond_json(ctx,
#            collections.OrderedDict(sorted(dict(
#                apiVersion = '1.0',
#                context = data['context'],
#                error = collections.OrderedDict(sorted(dict(
#                    code = 409,  # Conflict
#                    message = ctx._('Wrong version: {}, expected: {}').format(item_attributes.get('draft_id'),
#                        item.draft_id),
#                    ).iteritems())),
#                method = req.script_name,
#                params = inputs,
#                url = req.url.decode('utf-8'),
#                value = conv.check(conv.method('turn_to_json'))(item, state = ctx),
#                ).iteritems())),
#            headers = headers,
#            )
#    item = model.Item(**item_attributes)
#    item.save(ctx, safe = True)

#    return wsgihelpers.respond_json(ctx,
#        collections.OrderedDict(sorted(dict(
#            apiVersion = '1.0',
#            context = data['context'],
#            method = req.script_name,
#            params = inputs,
#            url = req.url.decode('utf-8'),
#            value = conv.check(conv.method('turn_to_json'))(item, state = ctx),
#            ).iteritems())),
#        headers = headers,
#        )


def extract_item_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        content = params.get('content'),
        description = params.get('description'),
        image_url = params.get('image_url'),
        rights = params.get('rights'),
        tag = params.getall('tag'),
        temporal_coverage_from = params.get('temporal_coverage_from'),
        temporal_coverage_to = params.get('temporal_coverage_to'),
        territorial_coverage = params.getall('territorial_coverage'),
        title = params.get('title'),
        url = params.get('url'),
        )


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    item, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Item.make_id_or_slug_to_instance(),
        )(req.urlvars.get('id_or_slug'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Item Error: {}').format(error))(
            environ, start_response)

    ctx.node = item

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
        (('GET', 'POST'), '^/delete/?$', admin_delete),
        (('GET', 'POST'), '^/edit/?$', admin_edit),
        ('GET', '^/toggle-lesson/?$', admin_toggle_lesson),
        )
    return router(environ, start_response)


def route_admin_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', admin_index),
        (('GET', 'POST'), '^/new/?$', admin_new),
        (None, '^/(?P<id_or_slug>[^/]+)(?=/|$)', route_admin),
        )
    return router(environ, start_response)


def route_api1(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    item, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Item.make_id_or_slug_to_instance(),
        )(req.urlvars.get('id_or_slug'), state = ctx)
    if error is not None:
        params = req.GET
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = params.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Item Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )(environ, start_response)

    ctx.node = item

    router = urls.make_router(
        ('DELETE', '^/?$', api1_delete),
        ('GET', '^/?$', api1_get),
        )
    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
        (('GET', 'POST'), '^/?$', api1_index),
#        ('POST', '^/upsert?$', api1_set),
        (None, '^/(?P<id_or_slug>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)
