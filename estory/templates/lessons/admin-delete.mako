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
from estory import model, urls
%>


<%inherit file="/site.mako"/>
<%namespace name="view" file="admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Lesson.get_admin_class_url(ctx)}">${_(u"Lessons")}</a></li>
            <li><a href="${lesson.get_admin_url(ctx)}">${lesson.get_title(ctx)}</a></li>
            <li class="active">${_(u'Delete')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${_(u'Deletion of {}').format(lesson.get_title(ctx))}</h2>
        <p class="confirm">${_(u"Are you sure that you want to delete this lesson?")}</p>
        <form method="post" action="${lesson.get_admin_url(ctx, 'delete')}">
            <%view:view_fields/>
            <button class="btn btn-danger" name="submit" type="submit"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</button>
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_(u'Delete')} - ${lesson.get_title(ctx)} - ${parent.title_content()}
</%def>

