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
from estory import conf, model, urls
%>


<%inherit file="/site.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Lesson.get_admin_class_url(ctx)}">${_(u"Lessons")}</a></li>
            <li><a href="${lesson.get_admin_url(ctx)}">${lesson.get_title(ctx)}</a></li>
            <li class="active">${_(u'Edit')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <form action="${lesson.get_admin_url(ctx, 'edit')}" method="post" role="form">
            <%self:hidden_fields/>
            <fieldset>
                <legend>${_(u'Edition of %s') % lesson.get_title(ctx)}</legend>
                <%self:error_alert/>
                <%self:form_fields/>
                <button class="btn btn-primary" name="submit" type="submit"><span class="glyphicon glyphicon-ok"></span> ${_('Save')}</button>
            </fieldset>
        </form>
</%def>


<%def name="form_fields()" filter="trim">
<%
    error = errors.get('title') if errors is not None else None
%>\
                <div class="form-group${' has-error' if error else ''}">
                    <label for="title">${_("Title")}</label>
                    <input class="form-control" id="title" name="title" required type="text" value="${inputs['title'] or ''}">
    % if error:
                    <span class="help-block">${error}</span>
    % endif
                </div>
<%
    error = errors.get('description') if errors is not None else None
%>\
                <div class="form-group${' has-error' if error else ''}">
                    <label for="description">${_("Description")}</label>
                    <textarea class="form-control" id="description" name="description">${
                        inputs['description'] or ''}</textarea>
    % if error:
                    <span class="help-block">${error}</span>
    % endif
                </div>
<%
    error = errors.get('image_url') if errors is not None else None
%>\
                <div class="form-group${' has-error' if error else ''}">
                    <label for="image_url">${_("Image URL")}</label>
                    <input class="form-control" id="image_url" name="image_url" type="url" value="${
                            inputs['image_url'] or ''}">
    % if error:
                    <span class="help-block">${error}</span>
    % endif
                </div>
<%
    tag_errors = errors.get('tag') if errors is not None else None
%>\
                <div class="form-group${' has-error' if error else ''}">
                    <label for="tag">${_("Tag")}</label>
                    <input class="form-control typeahead" id="tag" name="tag" type="text" value="${(inputs['tag'][0] if inputs['tag'] else None) or ''}">
<%
    error = tag_errors.get(0) if tag_errors is not None else None
%>\
    % if error:
                    <span class="help-block">${error}</span>
    % endif
                </div>
</%def>


<%def name="hidden_fields()" filter="trim">
</%def>


<%def name="title_content()" filter="trim">
${_(u'Edit')} - ${lesson.get_title(ctx)} - ${parent.title_content()}
</%def>

