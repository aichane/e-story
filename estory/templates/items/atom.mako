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
from estory import conf, model, texthelpers, urls
%>


<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${conf['realm']}</title>
    <id>${urls.get_full_url(ctx, 'api', '1', 'items', **urls.relative_query(inputs))}</id>
    <link href="${model.Item.get_admin_class_full_url(ctx) if data['target'] is None \
            else model.Item.get_class_back_url(ctx) if data['target'] == 'back' \
            else model.Item.get_class_front_url(ctx)}"/>
    <link href="${urls.get_full_url(ctx, 'api', '1', 'items', **urls.relative_query(inputs))}" rel="self"/>
##    <author>
##        <name>${_('e-story contributors')}</name>
##        <email>${conf['wenoit.email']}</email>
##        <uri>${conf['wenoit.url']}</uri>
##    </author>
##    % for tag in (tags or []):
##          <category term="${tag}"/>
##    % endfor
    <generator uri="http://github.com/etalab/e-story">e-story</generator>
    <rights>
        This feed is licensed under the Open Licence ${'<http://www.data.gouv.fr/Licence-Ouverte-Open-Licence>'}.
    </rights>
<%
    items = list(cursor)
    timestamp = max(
        item.timestamp
        for item in items
        )
%>\
    <updated>${timestamp.replace(u' ', u'Z')}</updated>
    % for item in items:
    <entry>
        <title>${item.title}</title>
        <id>${item.get_admin_full_url(ctx)}</id>
        <link href="${item.get_admin_full_url(ctx) if data['target'] is None \
                else item.get_back_url(ctx) if data['target'] == 'back' \
                else item.get_front_url(ctx)}"/>
<%
        organization = item.get_organization(ctx)
%>\
        % if organization is not None:
        <author>
            <name>${organization.title}</name>
            <uri>${organization.get_admin_full_url(ctx) if data['target'] is None \
                    else organization.get_back_url(ctx) if data['target'] == 'back' \
                    else organization.get_front_url(ctx)}</uri>
        </author>
        % endif
        % for tag in (item.tags or []):
        <category term="${tag['name']}"/>
        % endfor
        <updated>${item.timestamp.replace(u' ', u'Z')}</updated>
        % if item.notes:
        <summary type="html">
            ${texthelpers.htmlify_markdown(item.notes)}
        </summary>
        % endif
    </entry>
    % endfor
</feed>
