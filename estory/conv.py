# -*- coding: utf-8 -*-


# e-story -- Open data based history lessons
# By: Anael Ichane <anael.ichane@gmail.com>
#     Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 Anael Ichane & Emmanuel Raviart
# http://github.com/etalab/e-story
#
# This file is part of e-story.
#
# e-story is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# e-story is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Conversion functions"""


import re

from biryani1.baseconv import *
from biryani1.bsonconv import *
from biryani1.datetimeconv import *
from biryani1.objectconv import *
from biryani1.jsonconv import *
from biryani1.states import default_state, State


N_ = lambda message: message
year_or_month_or_day_re = re.compile(ur'[0-2]\d{3}(-(0[1-9]|1[0-2])(-([0-2]\d|3[0-1]))?)?$')


input_to_token = cleanup_line

input_to_year_or_month_or_day_str = pipe(
    cleanup_line,
    test(year_or_month_or_day_re.match, error = N_(u'Invalid year or month or day')),
    )


#json_to_item_attributes = pipe(
#    test_isinstance(dict),
#    struct(
#        dict(
#            id = pipe(
#                input_to_token,
#                not_none,
#                ),
#            ),
#        default = noop,  # TODO
#        ),
#    rename_item('id', '_id'),
#    )


def method(method_name, *args, **kwargs):
    def method_converter(value, state = None):
        if value is None:
            return value, None
        return getattr(value, method_name)(state or default_state, *args, **kwargs)
    return method_converter
