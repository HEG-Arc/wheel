# -*- coding: UTF-8 -*-
# models.py
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
from django.db import models

# Third-party app imports

# Appagoo imports


class Quiz(models.Model):
    code = models.CharField(unique=True, max_length=20)
    terminal = models.CharField(max_length=1)
    score = models.IntegerField(max_length=5, default=0)
    prize = models.ForeignKey('Prize', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'quiz'
        verbose_name_plural = 'quiz'
        ordering = ['-timestamp']

    def __unicode__(self):
        return self.code


class Prize(models.Model):
    index = models.IntegerField(max_length=2, help_text='The index of the prize on the wheel [0:n-1]')
    name = models.CharField(max_length=250, help_text='Name used for inventory purpose')
    label = models.CharField(max_length=250, help_text='This is the name displayed on the screen, with the article')
    percentage = models.IntegerField(max_length=2)
    stock = models.IntegerField(max_length=5)
    big = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'prize'
        verbose_name_plural = 'prizes'
        ordering = ['name']

    def __unicode__(self):
        return self.name