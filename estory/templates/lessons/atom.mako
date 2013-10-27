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
from estory import conf, model, texthelpers, urls
%>


<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${conf['realm']}</title>
    <id>${urls.get_full_url(ctx, 'api', '1', 'lessons', **urls.relative_query(inputs))}</id>
    <link href="${model.Lesson.get_admin_class_full_url(ctx) if data['target'] is None \
            else model.Lesson.get_class_back_url(ctx) if data['target'] == 'back' \
            else model.Lesson.get_class_front_url(ctx)}"/>
    <link href="${urls.get_full_url(ctx, 'api', '1', 'lessons', **urls.relative_query(inputs))}" rel="self"/>
##    <author>
##        <name>${_('e-story team')}</name>
##        <email>${conf['e-story.email']}</email>
##        <uri>${conf['e-story.url']}</uri>
##    </author>
##    % for tag in (tags or []):
##          <category term="${tag}"/>
##    % endfor
    <generator uri="https://github.com/aichane/e-story">e-story</generator>
    <rights>
        This feed is licensed under the Open Licence ${'<http://www.data.gouv.fr/Licence-Ouverte-Open-Licence>'}.
    </rights>
<%
    lessons = list(cursor)
    created = max(
        lesson.created
        for lesson in lessons
        )
%>\
    <updated>${created}Z</updated>
    % for lesson in lessons:
    <entry>
        <title>${lesson.title}</title>
        <id>${lesson.get_admin_full_url(ctx)}</id>
        <link href="${lesson.get_admin_full_url(ctx) if data['target'] is None \
                else lesson.get_back_url(ctx) if data['target'] == 'back' \
                else lesson.get_front_url(ctx)}"/>
        <updated>${lesson.created}Z</updated>
        % if lesson.description:
        <summary type="html">
            ${texthelpers.htmlify_markdown(lesson.description)}
        </summary>
        % endif
    </entry>
    % endfor
</feed>
