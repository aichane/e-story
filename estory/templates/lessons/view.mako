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
from estory import model, texthelpers


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


<%inherit file="/site.mako"/>


<%def name="breadcrumb()" filter="trim">
</%def>


<%def name="container_content()" filter="trim">
        <h2>${lesson.get_title(ctx)}</h2>
        <%self:view_fields/>
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
    % if items:
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
    % endif
</%def>

