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
import collections

import pymongo

from estory import model, texthelpers, urls
%>


<%inherit file="site.mako"/>


<%def name="breadcrumb()" filter="trim">
</%def>


<%def name="container_content()" filter="trim">
##        <div class="page-header">
##            <h1><%self:brand/></h1>
##        </div>
        <%self:jumbotron/>
</%def>


<%def name="jumbotron()" filter="trim">
<%
    user = model.get_user(ctx)
%>\
        <div class="jumbotron">
            <div class="container">
                <h2>${_(u"Welcome to e-story")}</h2>
                <p>${_(u"Open data based history lessons")}</p>
<%
    carousel_items = list(model.Item.find(
        dict(
            image_url = {'$exists': True},
            tags = u'accueil',
            ),
        as_class = collections.OrderedDict,
        ).sort([('name', pymongo.DESCENDING)]))
%>\
    % if carousel_items:
                <div id="carousel-example-generic" class="carousel slide">
                    <!-- Indicators -->
                    <ol class="carousel-indicators">
        % for item_index in range(len(carousel_items)):
                        <li data-target="#carousel-example-generic" data-slide-to="${item_index}"${
                                u' class="active"' if item_index == 0 else u'' | n}></li>
        % endfor
                    </ol>

                    <!-- Wrapper for slides -->
                    <div class="carousel-inner">
        % for item_index, item in enumerate(carousel_items):
                        <div class="item${u' active' if item_index == 0 else u''}">
                            <img alt="${item.title}" src="${item.image_url}">
                            <div class="carousel-caption">
            % if item.description is not None:
                                ${texthelpers.htmlify_markdown(item.description) | n}
            % endif
                            </div>
                        </div>
        % endfor
                    </div>

                    <!-- Controls -->
                    <a class="left carousel-control" href="#carousel-example-generic" data-slide="prev">
                        <span class="icon-prev"></span>
                    </a>
                    <a class="right carousel-control" href="#carousel-example-generic" data-slide="next">
                        <span class="icon-next"></span>
                    </a>
                </div>
    % endif
    % if user is None:
                <a class="btn btn-large btn-primary sign-in" href="#" title="${_(u'Sign in with Persona')}">${
                    _('Sign In')}</a>
    % endif
            </div>
        </div>
</%def>
