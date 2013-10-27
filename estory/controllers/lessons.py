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


"""Controllers for lessons"""


import collections
import datetime
import logging
import re

import pymongo
import webob
import webob.multidict

from .. import contexts, conv, model, paginations, templates, urls, wsgihelpers


inputs_to_lesson_data = conv.struct(
    dict(
        description = conv.cleanup_text,
        image_url = conv.make_input_to_url(full = True),
        tag = conv.pipe(
            conv.uniform_sequence(
                conv.input_to_slug,
                drop_none_items = True,
                ),
            conv.empty_to_none,
            ),
        title = conv.pipe(
            conv.cleanup_line,
            conv.not_none,
            ),
        ),
    default = 'drop',
    )
log = logging.getLogger(__name__)


@wsgihelpers.wsgify
def admin_activate(req):
    ctx = contexts.Ctx(req)
    lesson = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Edition unauthorized"),
            message = ctx._("You can not activate a lesson."),
            title = ctx._('Operation denied'),
            )
    if user._id != lesson.user_id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not activate a lesson."),
            title = ctx._('Operation denied'),
            )

    session = ctx.session
    session.lesson_id = lesson._id
    session.save(ctx, safe = True)

    # View lesson.
    return wsgihelpers.redirect(ctx, location = lesson.get_admin_url(ctx))


@wsgihelpers.wsgify
def admin_delete(req):
    ctx = contexts.Ctx(req)
    lesson = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Deletion unauthorized"),
            message = ctx._("You can not delete a lesson."),
            title = ctx._('Operation denied'),
            )
    if user._id != lesson.user_id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete a lesson."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        lesson.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.Lesson.get_admin_class_url(ctx))
    return templates.render(ctx, '/lessons/admin-delete.mako', lesson = lesson)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    lesson = ctx.node

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Edition unauthorized"),
            message = ctx._("You can not edit a lesson."),
            title = ctx._('Operation denied'),
            )
    if user._id != lesson.user_id and not user.admin:
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit a lesson."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            description = lesson.description,
            image_url = lesson.image_url,
            tag = lesson.tags,
            title = lesson.title,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_lesson_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_lesson_data(inputs, state = ctx)
        if errors is None:
            data['slug'], error = conv.pipe(
                conv.input_to_slug,
                conv.not_none,
                )(data['title'], state = ctx)
            if error is not None:
                errors = dict(title = error)
        if errors is None:
            if model.Lesson.find(
                    dict(
                        _id = {'$ne': lesson._id},
                        slug = data['slug'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(email = ctx._('A lesson with the same email already exists.'))
        if errors is None:
            data['tags'] = data.pop('tag')
            lesson.set_attributes(**data)
            if lesson.user_id is None or not user.admin:
                lesson.user_id = user._id
            lesson.save(ctx, safe = True)

            session = ctx.session
            session.lesson_id = lesson._id
            session.save(ctx, safe = True)

            # View lesson.
            return wsgihelpers.redirect(ctx, location = lesson.get_admin_url(ctx))
    return templates.render(ctx, '/lessons/admin-edit.mako', errors = errors, inputs = inputs, lesson = lesson)


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
                    conv.test_in(['slug', 'timestamp']),
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
        return wsgihelpers.not_found(ctx, explanation = ctx._('Lesson search error: {}').format(errors))

    criteria = {}
    if data['tag'] is not None:
        criteria['tags'] = re.compile(re.escape(data['tag']))
    if data['term'] is not None:
        criteria['slug'] = re.compile(re.escape(data['term']))
    if data['user'] is not None:
        criteria['user_id'] = data['user']._id
    cursor = model.Lesson.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'slug':
        cursor.sort([('slug', pymongo.ASCENDING)])
    elif data['sort'] == 'timestamp':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('slug', pymongo.ASCENDING)])
    lessons = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/lessons/admin-index.mako', data = data, errors = errors, lessons = lessons,
        inputs = inputs, pager = pager)


@wsgihelpers.wsgify
def admin_new(req):
    ctx = contexts.Ctx(req)

    user = model.get_user(ctx)
    if user is None:
        return wsgihelpers.unauthorized(ctx,
            explanation = ctx._("Creation unauthorized"),
            message = ctx._("You can not create a lesson."),
            title = ctx._('Operation denied'),
            )

    lesson = model.Lesson()
    if req.method == 'GET':
        errors = None
        inputs = extract_lesson_inputs_from_params(ctx)
    else:
        assert req.method == 'POST'
        inputs = extract_lesson_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_lesson_data(inputs, state = ctx)
        if errors is None:
            data['slug'], error = conv.pipe(
                conv.input_to_slug,
                conv.not_none,
                )(data['title'], state = ctx)
            if error is not None:
                errors = dict(title = error)
        if errors is None:
            if model.Lesson.find(
                    dict(
                        slug = data['slug'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(full_name = ctx._('A lesson with the same name already exists.'))
        if errors is None:
            data['tags'] = data.pop('tag')
            lesson.set_attributes(**data)
            lesson.user_id = user._id
            lesson.save(ctx, safe = True)

            session = ctx.session
            session.lesson_id = lesson._id
            session.save(ctx, safe = True)

            # View lesson.
            return wsgihelpers.redirect(ctx, location = lesson.get_admin_url(ctx))
    return templates.render(ctx, '/lessons/admin-new.mako', errors = errors, inputs = inputs, lesson = lesson)


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    lesson = ctx.node

    items = list(model.Item.find(
        dict(
            _id = {'$in': lesson.items_id},
            ),
        as_class = collections.OrderedDict,
        ).sort('temporal_coverage_from')) if lesson.items_id else []
    return templates.render(ctx, '/lessons/admin-view.mako', items = items, lesson = lesson)


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

    deleted_value = conv.check(conv.method('turn_to_json'))(ctx.node, state = ctx)
    ctx.node.delete(ctx, safe = True)

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

    cursor = model.Lesson.get_collection().find(None, [])
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = [
                lesson_attributes['_id']
                for lesson_attributes in cursor
                ],
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


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
            q = conv.cleanup_line,
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Lesson search error: {}').format(errors))

    criteria = {}
    if data['q'] is not None:
        criteria['title'] = re.compile(re.escape(data['q']))
    cursor = model.Lesson.get_collection().find(criteria, ['title'])
    return wsgihelpers.respond_json(ctx,
        [
            lesson_attributes['title']
            for lesson_attributes in cursor.limit(10)
            ],
        headers = headers,
        )


def extract_lesson_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        description = params.get('description'),
        image_url = params.get('image_url'),
        tag = params.getall('tag'),
        title = params.get('title'),
        )


@wsgihelpers.wsgify
def index(req):
    ctx = contexts.Ctx(req)

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
                    conv.test_in(['slug', 'timestamp']),
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
        return wsgihelpers.not_found(ctx, explanation = ctx._('Lesson search error: {}').format(errors))

    criteria = {}
    if data['tag'] is not None:
        criteria['tags'] = re.compile(re.escape(data['tag']))
    if data['term'] is not None:
        criteria['slug'] = re.compile(re.escape(data['term']))
    if data['user'] is not None:
        criteria['user_id'] = data['user']._id
    cursor = model.Lesson.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'slug':
        cursor.sort([('slug', pymongo.ASCENDING)])
    elif data['sort'] == 'timestamp':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('slug', pymongo.ASCENDING)])
    lessons = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/lessons/index.mako', data = data, errors = errors, lessons = lessons,
        inputs = inputs, pager = pager)


def route(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    lesson, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Lesson.make_id_or_slug_to_instance(),
        )(req.urlvars.get('id_or_slug'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Lesson Error: {}').format(error))(
            environ, start_response)

    ctx.node = lesson

    router = urls.make_router(
        ('GET', '^/?$', view),
        )
    return router(environ, start_response)


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    lesson, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Lesson.make_id_or_slug_to_instance(),
        )(req.urlvars.get('id_or_slug'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Lesson Error: {}').format(error))(
            environ, start_response)

    ctx.node = lesson

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
        (('GET', 'POST'), '^/activate/?$', admin_activate),
        (('GET', 'POST'), '^/delete/?$', admin_delete),
        (('GET', 'POST'), '^/edit/?$', admin_edit),
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

    lesson, error = conv.pipe(
        conv.input_to_slug,
        conv.not_none,
        model.Lesson.make_id_or_slug_to_instance(),
        )(req.urlvars.get('id_or_slug'), state = ctx)
    if error is not None:
        params = req.GET
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = params.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Lesson Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )(environ, start_response)

    ctx.node = lesson

    router = urls.make_router(
        ('DELETE', '^/?$', api1_delete),
        ('GET', '^/?$', api1_get),
        )
    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', api1_index),
        ('GET', '^/typeahead/?$', api1_typeahead),
        (None, '^/(?P<id_or_slug>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)


def route_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', index),
        (None, '^/(?P<id_or_slug>[^/]+)(?=/|$)', route),
        )
    return router(environ, start_response)


@wsgihelpers.wsgify
def view(req):
    ctx = contexts.Ctx(req)
    lesson = ctx.node

    items = list(model.Item.find(
        dict(
            _id = {'$in': lesson.items_id},
            ),
        as_class = collections.OrderedDict,
        ).sort('temporal_coverage_from')) if lesson.items_id else []
    return templates.render(ctx, '/lessons/view.mako', items = items, lesson = lesson)

