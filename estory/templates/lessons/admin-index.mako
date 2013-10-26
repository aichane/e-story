## -*- coding: utf-8 -*-


## e-story -- Open data based history lessons
## By: Anael Ichane <anael.ichane@gmail.com>
##     Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2013 Anael Ichane & Emmanuel Raviart
## http://github.com/etalab/e-story
##
## This file is part of e-story.
##
## e-story is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## e-story is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
from estory import model, texthelpers, urls
%>


<%inherit file="/object-admin-index.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li class="active">${_(u'Lessons')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <%self:search_form/>
    % if pager.item_count == 0:
        <h2>${_(u"No lesson found")}</h2>
    % else:
        % if pager.page_count > 1:
            % if pager.page_size == 1:
        <h2>${_(u"Lesson {0} of {1}").format(pager.first_item_number, pager.item_count)}</h2>
            % else:
        <h2>${_(u"Lessons {0} - {1} of {2}").format(pager.first_item_number, pager.last_item_number, pager.item_count)}</h2>
            % endif
        % elif pager.item_count == 1:
        <h2>${_(u"Single lesson")}</h2>
        % else:
        <h2>${_(u"{} lessons").format(pager.item_count)}</h2>
        % endif
        <%self:pagination object_class="${model.Lesson}" pager="${pager}"/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
                    <th>${_(u"User")}</th>
            % if data['sort'] == 'slug':
                    <th>${_(u"Title")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
            % else:
                    <th><a href="${model.Lesson.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'slug'))}">${_(u"Title")}</a></th>
            % endif
            % if data['sort'] == 'timestamp':
                    <th>${_(u"Last Modification")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
            % else:
                    <th><a href="${model.Lesson.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'timestamp'))}">${_(u"Last Modification")}</a></th>
            % endif
                </tr>
            </thead>
            <tbody>
        % for lesson in lessons:
                <tr>
                    <td>
<%
            user = lesson.get_user(ctx)
%>\
                        ${user.full_name if user is not None else lesson.user_id or u''}
                    </td>
                    <td>
                        <h4><a href="${lesson.get_admin_url(ctx)}">${lesson.title}</a></h4>
<%
            description_text = texthelpers.textify_markdown(lesson.description)
%>\
            % if description_text:
                        ${texthelpers.truncate(description_text, length = 180, whole_word = True)}
            % endif
                    </td>
                    <td>${lesson.timestamp or ''}</td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination object_class="${model.Lesson}" pager="${pager}"/>
    % endif
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${model.Lesson.get_admin_class_url(ctx, 'new')}">${_(u'New')}</a>
        </div>
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Lesson.get_admin_class_url(ctx)}" method="get" role="form">
    % if data['advanced_search']:
            <input name="advanced_search" type="hidden" value="1">
    % endif
            <input name="sort" type="hidden" value="${inputs['sort'] or ''}">
<%
    error = errors.get('term') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="term">${_("Term")}</label>
                <input class="form-control" id="term" name="term" type="text" value="${inputs['term'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
<%
    error = errors.get('tag') if errors is not None else None
    input_value = inputs['tag']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="tag">${_("Tag")}</label>
                <input class="form-control typeahead" id="tag" name="tag" type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('user') if errors is not None else None
    input_value = inputs['user']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="user">${_("User")}</label>
                <input class="form-control typeahead" id="user" name="user" type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-search"></span> ${
                _('Search')}</button>
##            <a href="${urls.get_url(ctx, 'api', '1', 'lessons', **urls.relative_query(inputs,
##                    advanced_search = None, format = 'atom', page = None, sort = None))}">${_('News Feed')}</a>
    % if data['advanced_search']:
            <a class="pull-right" href="${model.Lesson.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = None))}">${_('Simplified Search')}</a>
    % else:
            <a class="pull-right" href="${model.Lesson.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = 1))}">${_('Advanced Search')}</a>
    % endif
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Lessons')} - ${parent.title_content()}
</%def>

