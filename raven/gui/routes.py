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
from raven.footprinting.passive.dnsdumpster import DNSDumpsterAPI
from raven.footprinting.passive.geoip import GeoIPLookup
from raven.footprinting.passive.googledork import GoogleDork
from raven.footprinting.passive.reverseiplookup import ReverseIPLookup
from raven.footprinting.passive.waybackmachine import WayBackMachine
from raven.footprinting.passive.whoislookup import Whoislookup
from raven.footprinting.passive.subdomain import Subdomain


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
        if not details["ipstack"]:
            flash("API keys for ipstack not found.")
        if not details["ipinfo"]:
            flash("API keys for ipinfo not found.")
        return render_template('_geoip.html', title='Footprinting', details=module_details)

    elif name == "googledork":
        return render_template('_googledork.html', title='Footprinting', details=module_details)

    elif name == "reverseip":
        return render_template('_reverseip.html', title='Footprinting', details=module_details)

    elif name == "subdomain":
        return render_template('_subdomain.html', title='Footprinting', details=module_details)

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
    dnsdumpster_obj = DNSDumpsterAPI(domain)    
    result = dnsdumpster_obj.fetch()
    return jsonify(result)


@app.route('/_geoip/<name>', methods=['GET', 'POST'])
def geoip(name=None):
    ip = request.args.get('ip')
    details = get_details()
    geoip_obj = GeoIPLookup(ip)
    result = dict()
    if name == "Ipstack":
        result = geoip_obj.ipstack_api(details["ipstack"])
    elif name == "Ipinfo":
        result = geoip_obj.ipinfo_api(details["ipinfo"])
    elif name == "Hackertarget":
        result = geoip_obj.hackertarget_api()
    return jsonify(result)


@app.route('/_googledork', methods=['GET', 'POST'])
def googledork():
    domain = request.args.get('domainName')
    dork = request.args.get('dork')
    google_dork_obj= GoogleDork(domain)
    result = google_dork_obj.single_query(dork)
    return jsonify(result)


@app.route('/_reverseip/<name>', methods=['GET', 'POST'])
def reverseip(name=None):
    ip = request.args.get('ip')
    reverseip_obj = ReverseIPLookup(ip)
    if name == "yougetsignal":
        result = reverseip_obj.query_yougetsignal()
    elif name == "Hackertarget":
        result = reverseip_obj.query_hackertarget()
    return jsonify(result)


@app.route('/_subdomain/<name>', methods=['GET', 'POST'])
def subdomain(name=None):
    domain = request.args.get('domainName')
    subdomain_obj = Subdomain(domain)
    if name == "google_dork":
        result = subdomain_obj.google()
    elif name == "dnsdumpster":
        result = subdomain_obj.dnsdumpster()
    return jsonify(result)


@app.route('/_wayback', methods=['GET', 'POST'])
def wayback():
    domain = request.args.get('domainName')
    startYear = request.args.get('startYear')
    stopYear = request.args.get('stopYear')
    wayback_obj = WayBackMachine(domain)
    result = wayback_obj.get_urls(startYear, stopYear)
    return jsonify(result)



@app.route('/_whois/<name>', methods=['GET', 'POST'])
def whois(name=None):
    domain = request.args.get('domainName')
    ip = request.args.get('ip')
    whois_obj = Whoislookup()
    if name == "whois":
        result = whois_obj.whois_query(domain)
    elif name == "ipwhois":
        result = whois_obj.ip_whois_query(ip)

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
