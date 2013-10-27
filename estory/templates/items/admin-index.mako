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
            <li class="active">${_(u'Items')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <%self:search_form/>
    % if pager.item_count == 0:
        <h2>${_(u"No item found")}</h2>
    % else:
        % if pager.page_count > 1:
            % if pager.page_size == 1:
        <h2>${_(u"Item {0} of {1}").format(pager.first_item_number, pager.item_count)}</h2>
            % else:
        <h2>${_(u"Items {0} - {1} of {2}").format(pager.first_item_number, pager.last_item_number, pager.item_count)}</h2>
            % endif
        % elif pager.item_count == 1:
        <h2>${_(u"Single item")}</h2>
        % else:
        <h2>${_(u"{} items").format(pager.item_count)}</h2>
        % endif
        <%self:pagination object_class="${model.Item}" pager="${pager}"/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
                    <th>${_(u"Image")}</th>
            % if data['sort'] == 'slug':
                    <th>${_(u"Title")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
            % else:
                    <th><a href="${model.Item.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'slug'))}">${_(u"Title")}</a></th>
            % endif
            % if data['sort'] == 'temporal_coverage_from':
                    <th>${_(u"Period")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
            % else:
                    <th><a href="${model.Item.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'temporal_coverage_from'))}">${_(u"Period")}</a></th>
            % endif
                    <th>${_(u"Source")}</th>
            % if data['sort'] == 'timestamp':
                    <th>${_(u"Last Modification")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
            % else:
                    <th><a href="${model.Item.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'timestamp'))}">${_(u"Last Modification")}</a></th>
            % endif
                </tr>
            </thead>
            <tbody>
        % for item in items:
                <tr>
                    <td>
            % if item.image_url is not None:
                        <a href="${item.get_admin_url(ctx)}"><img class="img-responsive" style="max-width: 100px" src="${item.image_url}"></a>
            % endif
                    </td>
                    <td>
                        <h4><a href="${item.get_admin_url(ctx)}">${item.title}</a></h4>
<%
            description_text = texthelpers.textify_markdown(item.description)
%>\
            % if description_text:
                        ${texthelpers.truncate(description_text, length = 180, whole_word = True)}
            % endif
            % if item.temporal_coverage_from is not None or item.temporal_coverage_to is not None \
                    or item.territorial_coverage is not None:
                        <ul class="list-inline">
                % if item.temporal_coverage_from is not None or item.temporal_coverage_to is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Temporal coverage")}">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </a>
                    % if item.temporal_coverage_to:
                                ${_(u"{0} to {1}").format(item.temporal_coverage_from or _(u"…"), item.temporal_coverage_to)}
                    % else:
                                ${item.temporal_coverage_from}
                    % endif
                            </li>
                % endif
                % if item.territorial_coverage is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Territorial coverage")}">
                                    <span class="glyphicon glyphicon-globe"></span>
                                </a>
                                ${item.territorial_coverage}
                            </li>
                % endif
                        </ul>
            % endif
                    </td>
                    <td>${u' - '.join(
                        fragment
                        for fragment in (item.temporal_coverage_from, item.temporal_coverage_to)
                        if fragment
                        )}</td>
                    <td>
            % if item.user_id is None:
                        <img class="img-responsive" style="max-width: 100px" src="http://www.data.gouv.fr/var/data_gouv_fr/storage/images/producteurs/ministere-de-la-culture-et-de-la-communication/3246-4-fre-FR/Ministere-de-la-Culture-et-de-la-Communication_resultat.jpg">
            % else:
<%
                user = item.get_user(ctx)
%>\
                        ${user.full_name if user is not None else item.user_id or u''}
            % endif
                    </td>
                    <td>${item.timestamp.split('T')[0]}</td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination object_class="${model.Item}" pager="${pager}"/>
    % endif
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${model.Item.get_admin_class_url(ctx, 'new')}">${_(u'New')}</a>
        </div>
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Item.get_admin_class_url(ctx)}" method="get" role="form">
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
##            <a href="${urls.get_url(ctx, 'api', '1', 'items', **urls.relative_query(inputs,
##                    advanced_search = None, format = 'atom', page = None, sort = None))}">${_('News Feed')}</a>
    % if data['advanced_search']:
            <a class="pull-right" href="${model.Item.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = None))}">${_('Simplified Search')}</a>
    % else:
            <a class="pull-right" href="${model.Item.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = 1))}">${_('Advanced Search')}</a>
    % endif
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Items')} - ${parent.title_content()}
</%def>

