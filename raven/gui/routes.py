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
from flask import render_template, url_for, redirect, session, flash, request, jsonify
from sqlalchemy.exc import IntegrityError
from raven.gui.forms import InstanceForm, APIKeyForm, CMSForm
from raven.gui import app, db
from raven.gui.models import Instance
from raven.helper.apikey_handler import get_api_keys, update_keys

from raven.targets.instance import Instance as Target
from raven.footprinting.passive.cms import CMSDiscoveryPassive

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = InstanceForm()
    session.clear()
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
        session["instance_name"] = instance.name
        target = Target(instance.domain, instance.https)
        session["domain"] = target.domain
        session["https"] = target.https
        session["ip"] = target.get_ip()
        return render_template('dashboard.html', title='Dashboard', instance=instance)
    else:
        return redirect(url_for('home'))


def get_list(file_name: str):
    f = Path(__file__).parent.parent / 'data' / file_name
    keys = dict()

    with open(f) as f:
        data = json.load(f)
        keys.update(data)

    return keys


passive_modules_list = get_list('passive_footprinting.json')


@app.route('/footprinting', methods=['GET', 'POST'])
def footprinting():
    global passive_modules_list
    return render_template('footprinting.html', title='Footprinting', passive_list=passive_modules_list['passive'])


@app.route('/footprinting/passive/<name>', methods=['GET', 'POST'])
def passive(name=None):
    global passive_modules_list
    module_details = passive_modules_list["passive"][name]
    details = get_details()

    if session.get("instance_id"):
        if session["instance_id"]:
            flash(session["instance_name"] + " is active instance. All the results will be saved to database.")

    if name == "cms":
        if not details["whatcms"]:
            flash("API keys for whatcms not found.")
        return render_template('_cms.html', title='Footprinting', details=module_details)

    elif name == "dnsdumpster":
        return render_template('_dnsdumpster.html', title='Footprinting', details=module_details)

    elif name == "geoip":
        return render_template('_geoip.html', title='Footprinting', details=module_details)

    elif name == "googledork":
        return render_template('_googledork.html', title='Footprinting', details=module_details)

    elif name == "reverseip":
        return render_template('_reverseip.html', title='Footprinting', details=module_details)

    elif name == "wayback":
        return render_template('_wayback.html', title='Footprinting', details=module_details)

    elif name == "whois":
        return render_template('_whois.html', title='Footprinting', details=module_details)

    return render_template('footprinting.html')


@app.route('/_cms', methods=['GET', 'POST'])
def cms():
    domain = request.args.get('domainName')
    details = get_details()
    cms_obj = CMSDiscoveryPassive(details["whatcms"])
    result = cms_obj.query(domain)
    return jsonify(result)


@app.route('/_dnsdumpster', methods=['GET', 'POST'])
def dnsdumpster():
    domain = request.args.get('domainName')
    result = {}
    return jsonify(result)


@app.route('/_geoip', methods=['GET', 'POST'])
def geoip():
    ip = request.args.get('ip')
    details = get_details()
    result = {}
    return jsonify(result)


@app.route('/_googledork', methods=['GET', 'POST'])
def googledork():
    domain = request.args.get('domain')
    details = get_details()
    result = {}
    return jsonify(result)


@app.route('/_reverseip', methods=['GET', 'POST'])
def reverseip():
    ip = request.args.get('ip')
    details = get_details()
    result = {}
    return jsonify(result)



@app.route('/_wayback', methods=['GET', 'POST'])
def wayback():
    domain = request.args.get('domain')
    details = get_details()
    result = {}
    return jsonify(result)



@app.route('/_whois', methods=['GET', 'POST'])
def whois():
    domain = request.args.get('domain')
    ip = request.args.get('ip')
    details = get_details()
    result = {}
    return jsonify(result)


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
