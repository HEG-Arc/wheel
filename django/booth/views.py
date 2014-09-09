# -*- coding: UTF-8 -*-
# views.py
#
# Copyright (C) 2013 HES-SO//HEG Arc
#
# Author(s): Cédric Gaspoz <cedric.gaspoz@he-arc.ch>
#
# This file is part of Wheel.
#
# Wheel is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wheel is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wheel.  If not, see <http://www.gnu.org/licenses/>.

# Stdlib imports
import string
import logging
import time
import datetime
from random import randrange
import pysimpledmx
from threading import Thread

# Core Django imports
from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.conf import settings


# Third-party app imports

# Wheel imports
from .models import Prize, Quiz


SCORECODES = {
    'A': 0, 'B': 25, 'C': 50, 'D': 100, 'E': 200, 'F': 500
}

FREECODES = ['1A1', '2A2', '3A3']

ADMINCODES = {
    101: 'booth-admin-kids', 102: 'booth-admin-stats', 104: 'booth-admin-refresh', 105: 'booth-admin-light-off', 106: 'booth-admin-shutdown'
}

COM_PORT = '/dev/ttyUSB0'


def validate_code(code):
    # The code is in the form '32X242C3'
    code = code.lower()
    checksum = 0
    for char in code[:-1]:
        if char.isdigit():
            checksum += int(char)
        else:
            checksum += int(string.lowercase.index(char))
    if checksum % 10 == int(code[-1]):
        return True
    return False


def adscreen(request):
    return render_to_response('booth/adscreen.html', {
        'volume': str(settings.WHEEL_VOLUME),
    }, context_instance=RequestContext(request))


def scan(request, code):
    if validate_code(code):
        logging.info("Valid code received: %s" % code)
        # We test the code
        try:
            if code[-2] == 'Z' and int(code[:3]) in ADMINCODES:
                logging.debug("Admin code %s - %s" % (code[:3], ADMINCODES[int(code[:3])]))
                return HttpResponseRedirect(reverse(ADMINCODES[int(code[:3])]))
            elif code[-2] in SCORECODES:
                # We check if the code is already in the database
                try:
                    quiz = Quiz.objects.get(code=code)
                    if quiz.prize:
                        # This is a cheater ;-)
                        return HttpResponseRedirect(reverse('booth-cheater', args=(quiz.id,)))
                    else:
                        # Display the score
                        return HttpResponseRedirect(reverse('booth-score', args=(quiz.id,)))
                except Quiz.DoesNotExist:
                    quiz = Quiz(code=code, score=SCORECODES[code[-2]], terminal=code[0])
                    quiz.save()
                    return HttpResponseRedirect(reverse('booth-score', args=(quiz.id,)))
            else:
                # The code is invalid, sorry
                logging.warning("Code format not recognized: %s" % code)
                return HttpResponseRedirect(reverse('wrong-code', args=(code,)))
        except IndexError:
            return HttpResponseRedirect(reverse('wrong-code', args=('WRONG',)))
    else:
        logging.warning("Code is not valid: %s" % code)
        return HttpResponseRedirect(reverse('wrong-code', args=(code,)))


def score(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    return render_to_response('booth/score.html', {
        'quiz': quiz,
        'sound': 'good-job.ogg',
    }, context_instance=RequestContext(request))


def prize(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    past_prize = int(request.session.get('prize', 12))
    logging.info("Past_prize: %s" % past_prize)
    random_prize = get_random_prize(past_prize)
    quiz.prize = random_prize
    quiz.save()
    random_prize.stock -= 1
    random_prize.save()
    request.session['prize'] = random_prize.id
    return render_to_response('booth/prize.html', {
        'quiz': quiz,
        'prize': random_prize,
    }, context_instance=RequestContext(request))


def prize_kids(request):
    past_prize = int(request.session.get('prize', 12))
    logging.info("Past_prize: %s" % past_prize)
    random_prize = get_random_prize(past_prize)
    random_prize.stock -= 1
    random_prize.save()
    request.session['prize'] = random_prize.id
    return render_to_response('booth/prize.html', {
        'prize': random_prize,
    }, context_instance=RequestContext(request))


def cheater(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    return render_to_response('booth/cheater.html', {
        'quiz': quiz,
    }, context_instance=RequestContext(request))


def wrong(request, code):
    return render_to_response('booth/wrong.html', {
        'code': code,
    }, context_instance=RequestContext(request))


def get_random_prize(past_prize):
    prizes_list = Prize.objects.all().filter(stock__gt=0)
    # We build a dict with all available prizes
    prizes_dict = {}
    total_percent = 0
    for prize in prizes_list:
        prizes_dict[prize.id] = prize.percentage
        if prize.percentage != 100:
            total_percent += prize.percentage
    # We build a list with all prizes
    weighted_prizes_list = []
    for p in prizes_dict:
        if prizes_dict[p] != 100:
            for i in range(0, prizes_dict[p]):
                weighted_prizes_list.append(p)
        else:
            for i in range(0, 100-total_percent):
                weighted_prizes_list.append(p)
    # We randomly choose one prize in the list
    prize = past_prize
    while prize == past_prize:
        prize = weighted_prizes_list[randrange(len(weighted_prizes_list))]
        logging.info("Random prize: %s" % prize)
    random_prize = get_object_or_404(Prize, pk=prize)
    return random_prize


def admin_stats(request):
    from suremark import printpos
    htmlstring = u"<center><em>Capa'cité 2014</em><br>%s<br><br><font face='A'>" % datetime.datetime.now()
    stock = Prize.objects.all()
    htmlstring += u"<left><br><b><u>Stock actuel</u></b><br>"
    for prize in stock:
        htmlstring += u"<left>%s<right>%s<br>" % (prize.name, prize.stock)
    quizz = Quiz.objects.filter(timestamp__gte=datetime.date.today()).values('terminal').annotate(qty=Count('prize')).order_by('terminal')
    htmlstring += u"<br><left><b><u>Statistiques de la journée</u></b><br>"
    for q in quizz:
        htmlstring += u"<left>Borne %s<right>%s<br>" % (q['terminal'], q['qty'])
    total = Quiz.objects.all().count()
    htmlstring += u"<br><left><b><u>Statistiques du salon</u></b><br>"
    htmlstring += u"<left>Nombre de participants<right>%s<br>" % total
    htmlstring += u"<br><br><br><br><br><cut>"
    printpos(htmlstring)
    return HttpResponseRedirect(reverse('booth-adscreen'))


def admin_refresh(request):
    return HttpResponseRedirect(reverse('booth-adscreen'))


def admin_shutdown(request):
    t = Thread(target=admin_shutdown_thread)
    t.start()
    return render_to_response('booth/shutdown.html', {
    }, context_instance=RequestContext(request))


def admin_shutdown_thread():
    from subprocess import call
    call("sudo shutdown -h now", shell=True)


def light_ambiant(request):
    t = Thread(target=light_ambiant_thread)
    t.start()
    return HttpResponse("OK: Ambiant", content_type="text/plain")


def light_ambiant_thread():
    mydmx = pysimpledmx.DMXConnection(COM_PORT)
    mydmx.setChannel(1, 0) # set DMX channel 1 Red (0-255)
    mydmx.setChannel(2, 138) # set DMX channel 2 Green (0-255)
    mydmx.setChannel(3, 201)   # set DMX channel 3 Blue (0-255)
    mydmx.setChannel(4, 0)   # set DMX channel 4 Macro 0
    mydmx.setChannel(5, 0)   # set DMX channel 5 Strobe (16-255)
    mydmx.setChannel(6, 0)   # set DMX channel 6 Mode 0
    mydmx.setChannel(7, 150)   # set DMX channel 7 Dim (0-255)
    mydmx.setChannel(8, 0) # set DMX channel 1 Red (0-255)
    mydmx.setChannel(9, 138) # set DMX channel 2 Green (0-255)
    mydmx.setChannel(10, 201)   # set DMX channel 3 Blue (0-255)
    mydmx.setChannel(11, 0)   # set DMX channel 4 Macro 0
    mydmx.setChannel(12, 0)   # set DMX channel 5 Strobe (16-255)
    mydmx.setChannel(13, 0)   # set DMX channel 6 Mode 0
    mydmx.setChannel(14, 100)   # set DMX channel 7 Dim (0-255)
    mydmx.render()           # render all of the above changes onto the DMX network


def light_roulette(request):
    t = Thread(target=light_roulette_thread)
    t.start()
    return HttpResponse("OK: Roulette", content_type="text/plain")


def light_roulette_thread():
    mydmx = pysimpledmx.DMXConnection(COM_PORT)
    mydmx.setChannel(1, 0) # set DMX channel 1 Red
    mydmx.setChannel(2, 138) # set DMX channel 2 Green
    mydmx.setChannel(3, 201)   # set DMX channel 3 Blue
    mydmx.setChannel(4, 0)   # set DMX channel 4 Dimmer
    mydmx.setChannel(5, 255)   # set DMX channel 5 Strobe
    mydmx.setChannel(6, 0)   # set DMX channel 5 Strobe
    mydmx.setChannel(7, 255)   # set DMX channel 5 Strobe
    mydmx.setChannel(8, 230) # set DMX channel 1 Red (0-255)
    mydmx.setChannel(9, 0) # set DMX channel 2 Green (0-255)
    mydmx.setChannel(10, 98)   # set DMX channel 3 Blue (0-255)
    mydmx.setChannel(11, 0)   # set DMX channel 4 Macro 0
    mydmx.setChannel(12, 255)   # set DMX channel 5 Strobe (16-255)
    mydmx.setChannel(13, 0)   # set DMX channel 6 Mode 0
    mydmx.setChannel(14, 150)   # set DMX channel 7 Dim (0-255)
    mydmx.render()           # render all of the above changes onto the DMX network
    for i in [180, 120, 50, 16]:
        time.sleep(2)
        mydmx.setChannel(5, i)   # set DMX channel 5 Strobe
        mydmx.setChannel(12, i)   # set DMX channel 5 Strobe
        mydmx.render()           # render all of the above changes onto the DMX network


def light_win(request):
    t = Thread(target=light_win_thread)
    t.start()
    return HttpResponse("OK: Win", content_type="text/plain")


def light_win_thread():
    mydmx = pysimpledmx.DMXConnection(COM_PORT)
    mydmx.setChannel(8, 230) # set DMX channel 1 Red (0-255)
    mydmx.setChannel(9, 0) # set DMX channel 2 Green (0-255)
    mydmx.setChannel(10, 98)   # set DMX channel 3 Blue (0-255)
    mydmx.setChannel(11, 0)   # set DMX channel 4 Macro 0
    mydmx.setChannel(12, 0)   # set DMX channel 5 Strobe (16-255)
    mydmx.setChannel(13, 0)   # set DMX channel 6 Mode 0
    mydmx.setChannel(14, 150)   # set DMX channel 7 Dim (0-255)
    mydmx.render()
    for i in range(1, 6):
        mydmx.setChannel(1, 0) # set DMX channel 1 Red
        mydmx.setChannel(2, 138) # set DMX channel 2 Green
        mydmx.setChannel(3, 201)   # set DMX channel 3 Blue
        mydmx.setChannel(4, 0)   # set DMX channel 4 Dimmer
        mydmx.setChannel(5, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(6, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(7, 255)   # set DMX channel 5 Strobe
        mydmx.render()           # render all of the above changes onto the DMX network
        time.sleep(0.2)
        mydmx.setChannel(1, 239) # set DMX channel 1 Red
        mydmx.setChannel(2, 130) # set DMX channel 2 Green
        mydmx.setChannel(3, 20)   # set DMX channel 3 Blue
        mydmx.setChannel(4, 0)   # set DMX channel 4 Dimmer
        mydmx.setChannel(5, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(6, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(7, 255)   # set DMX channel 5 Strobe
        mydmx.render()           # render all of the above changes onto the DMX network
        time.sleep(0.2)
        mydmx.setChannel(1, 230) # set DMX channel 1 Red
        mydmx.setChannel(2, 0) # set DMX channel 2 Green
        mydmx.setChannel(3, 98)   # set DMX channel 3 Blue
        mydmx.setChannel(4, 0)   # set DMX channel 4 Dimmer
        mydmx.setChannel(5, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(6, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(7, 255)   # set DMX channel 5 Strobe
        mydmx.render()           # render all of the above changes onto the DMX network
        time.sleep(0.2)
        mydmx.setChannel(1, 123) # set DMX channel 1 Red
        mydmx.setChannel(2, 170) # set DMX channel 2 Green
        mydmx.setChannel(3, 32)   # set DMX channel 3 Blue
        mydmx.setChannel(4, 0)   # set DMX channel 4 Dimmer
        mydmx.setChannel(5, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(6, 0)   # set DMX channel 5 Strobe
        mydmx.setChannel(7, 255)   # set DMX channel 5 Strobe
        mydmx.render()           # render all of the above changes onto the DMX network
        time.sleep(0.2)
    mydmx.setChannel(1, 0) # set DMX channel 1 Red
    mydmx.setChannel(2, 138) # set DMX channel 2 Green
    mydmx.setChannel(3, 201)   # set DMX channel 3 Blue
    mydmx.setChannel(4, 0)   # set DMX channel 4 Dimmer
    mydmx.setChannel(5, 0)   # set DMX channel 5 Strobe
    mydmx.setChannel(6, 0)   # set DMX channel 5 Strobe
    mydmx.setChannel(7, 150)   # set DMX channel 5 Strobe
    mydmx.setChannel(8, 0) # set DMX channel 1 Red (0-255)
    mydmx.setChannel(9, 138) # set DMX channel 2 Green (0-255)
    mydmx.setChannel(10, 201)   # set DMX channel 3 Blue (0-255)
    mydmx.setChannel(11, 0)   # set DMX channel 4 Macro 0
    mydmx.setChannel(12, 0)   # set DMX channel 5 Strobe (16-255)
    mydmx.setChannel(13, 0)   # set DMX channel 6 Mode 0
    mydmx.setChannel(14, 100)   # set DMX channel 7 Dim (0-255)
    mydmx.render()           # render all of the above changes onto the DMX network


def light_off(request):
    t = Thread(target=light_off_thread)
    t.start()
    return HttpResponseRedirect(reverse('booth-adscreen'))


def light_off_thread():
    mydmx = pysimpledmx.DMXConnection(COM_PORT)
    mydmx.setChannel(7, 0)   # set DMX channel 4 Dimmer
    mydmx.setChannel(14, 0)   # set DMX channel 4 Dimmer
    mydmx.render()           # render all of the above changes onto the DMX network
    #mydmx.setChannel(4, 255, autorender=True) # set channel 4 to full and render to the network