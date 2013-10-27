## -*- coding: utf-8 -*-


## e-story -- Open data based history lessons
## By: Anael Ichane <anael.ichane@gmail.com>
##     Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2013 Anael Ichane & Emmanuel Raviart
## http://github.com/aichane/e-story
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


<%inherit file="/object-admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Item.get_admin_class_url(ctx)}">${_(u"Items")}</a></li>
            <li class="active">${item.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${item.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
<%
    session = ctx.session
    lesson = session.get_lesson(ctx) if session is not None else None
%>\
    % if lesson is not None:
            <a class="btn btn-success" href="${item.get_admin_url(ctx, 'toggle-lesson')}">${
                _(u'Remove from Lesson') if item._id in (lesson.items_id or []) else _(u'Add to Lesson')}</a>
    % endif
##            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'items', item.slug)}">${_(u'JSON')}</a>
            <a class="btn btn-default" href="${item.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
            <a class="btn btn-danger"  href="${item.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${item.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${item.title}</div>
        </div>
<%
    value = item.description
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
            <div class="col-sm-10">
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" href="#description-view">${_(u"View")}</a></li>
                    <li><a data-toggle="tab" href="#description-source">${_(u"Source")}</a></li>
                </ul>
                <div class="tab-content">
                    <div class="active tab-pane" id="description-view">
                        ${texthelpers.htmlify_markdown(value) | n}
                    </div>
                    <div class="tab-pane" id="description-source">
                        <pre class="break-word">${value}</pre>
                    </div>
                </div>
            </div>
        </div>
    % endif
<%
    value = item.image_url
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
            <div class="col-sm-10"><img class="img-responsive" src="${value}"></div>
        </div>
    % endif
<%
    value = item.url
%>\
    % if value is not None:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("URL"))}</b></div>
                    <div class="col-sm-10"><a href="${value}" target="_blank">${value}</a></div>
                </div>
    % endif
<%
    value = item.content
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("HTML Fragment"))}</b></div>
            <div class="col-sm-10">
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" href="#content-view">${_(u"View")}</a></li>
                    <li><a data-toggle="tab" href="#content-source">${_(u"Source")}</a></li>
                </ul>
                <div class="tab-content">
                    <div class="active tab-pane" id="content-view">
                        ${texthelpers.clean_html(value) | n}
                    </div>
                    <div class="tab-pane" id="content-source">
                        <pre class="break-word">${value}</pre>
                    </div>
                </div>
            </div>
        </div>
    % endif
<%
    value = item.temporal_coverage_from
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Temporal Coverage From"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
    % endif
<%
    value = item.temporal_coverage_to
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Temporal Coverage To"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
    % endif
<%
    value = item.territorial_coverage
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Territorial Coverage"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
    % endif
    % if item.tags:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Tags"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for tag in item.tags:
            <li class="list-group-item">
<%
            value = tag
%>\
                <a href="${model.Item.get_admin_class_url(ctx, tag = value)}">${value}</a>
            </li>
        % endfor
            </ul>
        </div>
    % endif
<%
    value = item.user_id
    user = item.get_user(ctx)
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("User"))}</b></div>
            <div class="col-sm-10">
            % if user is None:
                ${value}
            % else:
                <a href="${user.get_admin_url(ctx)}">${user.full_name}</a>
            % endif
            </div>
        </div>
    % endif
<%
    value = item.timestamp
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Last Modification"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
    % endif
</%def>

