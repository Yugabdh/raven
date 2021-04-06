#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        routes
# Purpose:     routes for URLs
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import time
import calendar

from flask import render_template
from raven.gui import app
from raven.gui.forms import InstanceForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = InstanceForm()
    if form.validate_on_submit():
        if form.https.data:
            https = True
        else:
            https = False
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        data = {
            "instance_name": form.instance_name.data,
            "domain": form.domain.data,
            "https": https,
            "note": form.note.data,
            "creation_time": ts,
        }
        print(data)

    return render_template('home.html', form=form)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


@app.route('/notification')
def notification():
    return render_template('notification.html', title='Notification')


@app.route('/settings')
def settings():
    return render_template('settings.html', title='Settings')

