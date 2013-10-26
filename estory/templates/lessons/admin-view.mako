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
import collections

from estory import model, texthelpers, urls


def get_end_date(item):
    if item.temporal_coverage_to is None:
        hyphen_count = item.temporal_coverage_from.count('-')
        if hyphen_count >= 2:
            return item.temporal_coverage_from
        if hyphen_count == 1:
            return u'{}-31'.format(item.temporal_coverage_from)  # Wrong for months with less than 31 days
        return u'{}-12-31'.format(item.temporal_coverage_from)
    hyphen_count = item.temporal_coverage_to.count('-')
    if hyphen_count >= 2:
        return item.temporal_coverage_to
    if hyphen_count == 1:
        return u'{}-31'.format(item.temporal_coverage_to)  # Wrong for months with less than 31 days
    return u'{}-12-31'.format(item.temporal_coverage_to)


def get_start_date(item):
    hyphen_count = item.temporal_coverage_from.count('-')
    if hyphen_count >= 2:
        return item.temporal_coverage_from
    if hyphen_count == 1:
        return u'{}-01'.format(item.temporal_coverage_from)
    return u'{}-01-01'.format(item.temporal_coverage_from)
%>


<%inherit file="/object-admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Lesson.get_admin_class_url(ctx)}">${_(u"Lessons")}</a></li>
            <li class="active">${lesson.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${lesson.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
##            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'lessons', lesson.slug)}">${_(u'JSON')}</a>
            <a class="btn btn-default" href="${lesson.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
            <a class="btn btn-danger"  href="${lesson.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="scripts()" filter="trim">
    <%parent:scripts/>
    <script>
var timelineData = {
    timeline: {
        asset: ${dict(
#            caption = 'Caption text goes here',
#            credit = 'Credit Name Goes Here',
            media = lesson.image_url,
            ) | n, js},
        "date": ${[
            dict(
                asset = dict(
#                    caption = 'Caption text goes here',
#                    credit = 'Credit Name Goes Here',
                    media = item.image_url,
                    thumbnail = item.image_url,
                    ),
#                "classname":"optionaluniqueclassnamecanbeaddedhere",
                endDate = get_end_date(item).replace('-', ','),
                headline = item.title,
                startDate = get_start_date(item).replace('-', ','),
                tag = item.tags[0] if item.tags else None,
                text = u'{}<div style="font-family: Helvetica Neue,Helvetica,Arial,sans-serif"><a class="btn btn-primary" data-toggle="modal" href="#{}-modal" style="color: rgb(255, 255, 255); margin-left: 5px; padding: 6px 12px; margin-bottom: 0px; font-size: 14px; font-weight: normal;">{}</a></div>'.format(
                    texthelpers.htmlify_markdown(item.description),
                    item.slug,
                    _(u'View'),
                    ),
                )
            for item in items
            ] | n, js},
##        "era": [
##            {
##                "startDate":"2011,12,10",
##                "endDate":"2011,12,11",
##                "headline":"Headline Goes Here",
##                "text":"<p>Body text goes here, some HTML is OK</p>",
##                "tag":"This is Optional"
##            }
##        ],
        headline: ${lesson.title | n, js},
    % if lesson.description:
        text: ${texthelpers.htmlify_markdown(lesson.description) | n, js},
    % endif
        type: 'default'
    }
};


$(function() {
    createStoryJS({
        lang: ${ctx.lang[0].split('-', 1)[0] | n, js},
        type: 'timeline',
        width: '100%',
        height: '600',
        source: timelineData,
        embed_id: 'lesson-timeline'
    });
});
    </script>
</%def>


<%def name="title_content()" filter="trim">
${lesson.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${lesson.title}</div>
        </div>
<%
    value = lesson.description
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
    value = lesson.image_url
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
            <div class="col-sm-10"><img class="img-responsive" src="${value}"></div>
        </div>
    % endif
    % if items:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Items"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for item in items:
            <li class="list-group-item">
                <a href="${item.get_admin_url(ctx)}">${item.title}</a>
            </li>
        % endfor
            </ul>
            <div class="col-sm-offset-2 col-sm-10">
                <div id="lesson-timeline"></div>
        % for item in items:
                <div class="modal fade" id="${item.slug}-modal" tabindex="-1" role="dialog" aria-labelledby="${
                        item.slug}-modal-title" aria-hidden="true">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                                <h4 class="modal-title" id="${item.slug}-modal-title">
            % if item.url:
                                    <a href="${item.url}" target="_blank">${item.title}</a>
            % else:
                                    ${item.title}
            % endif
                                </h4>
                            </div>
                            <div class="modal-body">
            % if item.description:
                                ${texthelpers.htmlify_markdown(item.description) | n}
            % endif
            % if item.image_url:
                                <img class="img-responsive" src="${item.image_url}">
            % endif
            % if item.content:
                                ${texthelpers.clean_html(item.content) | n}
            % endif
                            </div>
                            <div class="modal-footer">
                            <button type="button" class="btn btn-primary" data-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
        % endfor
            </div>
        </div>
    % endif
    % if lesson.tags:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Tags"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for tag in lesson.tags:
            <li class="list-group-item">
<%
            value = tag
%>\
                <a href="${model.Lesson.get_admin_class_url(ctx, tag = value)}">${value}</a>
            </li>
        % endfor
            </ul>
        </div>
    % endif
<%
    value = lesson.user_id
    user = lesson.get_user(ctx)
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
    value = lesson.timestamp
%>\
    % if value is not None:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Last Modification"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
    % endif
</%def>

