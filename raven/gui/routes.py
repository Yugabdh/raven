#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        routes
# Purpose:     routes for URLs
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

import socket
import os
import json

from pathlib import Path
from flask import render_template, url_for, redirect, session, flash
from sqlalchemy.exc import IntegrityError
from raven.gui.forms import InstanceForm, APIKeyForm
from raven.gui import app, db
from raven.gui.models import Instance
from raven.helper.apikey_handler import get_api_keys, update_keys


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = InstanceForm()
    instance_list = Instance.query.all()
    if form.validate_on_submit():
        if form.https.data:
            https = True
        else:
            https = False

        instance = Instance(name=form.instance_name.data, domain=form.domain.data, https=https, notes=form.note.data)
        try:
            db.session.add(instance)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # error, there already is a Instance with same name
            # constraint failed
            flash("This instance name already exists. Try another instance name.")

        if instance.id:
            session["instance_name"] = form.instance_name.data
            session["instance_id"] = instance.id
            return redirect(url_for('dashboard', instance_id=instance.id))

    return render_template('home.html', form=form, instance_list=instance_list)

@app.route('/instances')
def instances():
    instance_list = Instance.query.all()
    return render_template('instances.html', title='Instances', instance_list=instance_list)

@app.route('/dashboard/<instance_id>', methods=['GET', 'POST'])
def dashboard(instance_id=None):
    if instance_id:
        session["instance_id"] = instance_id
        instance = Instance.query.get_or_404(instance_id)
        # instance_data = db.select([instance]).where(instance.columns.sex == 'F')
        return render_template('dashboard.html', title='Dashboard', instance=instance)
    else:
        return redirect(url_for('home'))


@app.route('/notification')
def notification():
    return render_template('notification.html', title='Notification')


def get_details():
    """
    Get device details about network and os
    :return: dictionary with details
    """

    details = dict()
    keys = get_api_keys()
    details.update(keys)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        details["host_name"] = socket.gethostname()
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        details["host_ip"] = s.getsockname()[0]
        if os.geteuid():
            details["user_level"] = "Not root"
        else:
            details["user_level"] = "root"

    except socket.error as e:
        print("[!] Unable to get Hostname and IP")
        print(e)

    return details


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form = APIKeyForm()
    details = get_details()
    if form.validate_on_submit():
        keys = {
            "ipstack": form.ipstack.data,
            "ipinfo": form.ipinfo.data,
            "whatcms": form.whatcms.data
        }
        update_keys(keys)
        details = get_details()
        flash("API keys update.")
    return render_template('settings.html', title='Settings', details=details, form=form)
