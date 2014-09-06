# -*- coding: UTF-8 -*-
# urls.py
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
from django.conf.urls import patterns, url

# Third-party app imports

# Appagoo imports
from . import views

urlpatterns = patterns('',
    url(r'^$', views.adscreen, name='booth-adscreen'),
    url(r'^scan/(?P<code>\w+)/$', views.scan, name='booth-scan'),
    url(r'^score/(?P<quiz_id>\d+)/$', views.score, name='booth-score'),
    url(r'^prize/(?P<quiz_id>\d+)/$', views.prize, name='booth-prize'),
    url(r'^cheater/(?P<quiz_id>\d+)/$', views.cheater, name='booth-cheater'),
    url(r'^wrong/(?P<code>\w+)/$', views.wrong, name='wrong-code'),
    url(r'^light/roulette/$', views.light_roulette, name='light-roulette'),
    url(r'^light/ambiant/$', views.light_ambiant, name='light-ambiant'),
    url(r'^light/win/$', views.light_win, name='light-win'),
    url(r'^light/off/$', views.light_off, name='light-off'),
)
