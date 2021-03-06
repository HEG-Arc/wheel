# -*- coding: UTF-8 -*-
# admin.py
#
# Copyright (C) 2013 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of appagoo.
#
# appagoo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# appagoo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with appagoo.  If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports

# Core Django imports
from django.contrib import admin

# Third-party app imports

# Appagoo imports
from .models import Prize, Quiz


class PrizeAdmin(admin.ModelAdmin):
    list_display = ('index', 'name', 'percentage', 'stock', 'big')


class QuizAdmin(admin.ModelAdmin):
    list_display = ('code', 'score', 'terminal', 'prize', 'timestamp')
    pass

admin.site.register(Prize, PrizeAdmin)
admin.site.register(Quiz, QuizAdmin)