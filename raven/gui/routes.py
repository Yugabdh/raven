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
from raven.gui.forms import InstanceForm, APIKeyForm
from raven.gui import app, db
from raven.gui.models import Instance, Footprint
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

from raven.footprinting.active.traceroute import Traceroute
from raven.footprinting.active.buildwith import BuildWith
from raven.footprinting.active.robot_sitemap import Robot_sitemap
from raven.footprinting.active.sslinfo import SSL
from raven.footprinting.active.webserver_detect import Webserver_detect

from raven.footprinting.osint.nmap_auto import Nmap_auto


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
        except Exception as e:
            print(e)

        if instance.id:
            session["instance_name"] = form.instance_name.data
            session["instance_id"] = instance.id
            session["domain"] = form.domain.data
            return redirect(url_for('dashboard', instance_id=instance.id))

    return render_template('home.html', form=form, instance_list=instance_list)


@app.route('/instances')
def instances():
    session.clear()
    instance_list = Instance.query.all()
    return render_template('instances.html', title='Instances', instance_list=instance_list)


@app.route('/dashboard/<instance_id>', methods=['GET', 'POST'])
def dashboard(instance_id=None):
    if instance_id:
        session["instance_id"] = instance_id

        instance = Instance.query.get_or_404(instance_id)
        session["instance_name"] = instance.name
        target = Target(instance.domain, instance.https)
        # If ip address exists in session no need to create target object
        # This is to avoid unnecessary
        # connection to server(To get server IP address we create socket and connect to server)
        if session.get("ip"):
            if session.get("domain"):
                if session["domain"] != target.domain:
                    session["ip"] = target.get_ip()
        else:
            session["ip"] = target.get_ip()
        session["domain"] = target.domain
        session["https"] = target.https

        # Fetching footprinting results of active instance
        footprint = footprinting_get_data(session["instance_id"])
        footprint_results = list()
        for _ in footprint:
            data = dict()
            data["id"] = _.id
            data["type_recon"] = _.type_recon
            data["module_name"] = _.module_name
            data["params_value"] = _.params_value
            data["overflow"] = _.overflow
            data["scan_time"] = _.scan_time
            data["result"] = _.result
            data["instance_id"] = _.instance_id
            footprint_results.append(data)
        return render_template('dashboard.html', title='Dashboard', instance=instance,
                               footprint_results=footprint_results)
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
active_modules_list = get_list('active_footprinting.json')
enumeration_modules_list = get_list('enumeration.json')


@app.route('/footprinting', methods=['GET', 'POST'])
def footprinting():
    global passive_modules_list
    global active_modules_list
    return render_template('footprinting.html', title='Footprinting', passive_list=passive_modules_list['passive'],
                           active_list=active_modules_list["active"])


@app.route('/footprinting/passive/<name>', methods=['GET', 'POST'])
def passive(name=None):
    global passive_modules_list
    module_details = passive_modules_list["passive"][name]
    details = get_details()

    if session.get("instance_id"):
        flash("'" + session["instance_name"] + "' is active instance. All the results will be saved to database.")

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


def footprint_save_to_db(type_recon, module_name, params_value, overflow, result, instance_id):
    footprint = Footprint(type_recon=type_recon, module_name=module_name, params_value=params_value, overflow=overflow,
                          result=result, instance_id=instance_id)
    try:
        db.session.add(footprint)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def footprinting_get_data(instance_id):
    data = Footprint.query.filter_by(instance_id=instance_id).all()
    return data


@app.route('/_cms', methods=['GET', 'POST'])
def cms():
    domain = request.args.get('domainName')
    details = get_details()
    cms_obj = CMSDiscoveryPassive(details["whatcms"])
    result = cms_obj.query(domain)        
    if session.get("instance_id") and result["code"] == 200:
        footprint_save_to_db("Passive", "cms", f"'Domain': '{domain}'", False, json.dumps(result),
                             session["instance_id"])
    return jsonify(result)


@app.route('/_dnsdumpster', methods=['GET', 'POST'])
def dnsdumpster():
    domain = request.args.get('domainName')
    dnsdumpster_obj = DNSDumpsterAPI(domain)
    result = dnsdumpster_obj.fetch()
    if result:
        temp_txt = list()
        if 'txt' in result['dns_records'].keys():
            for _ in result['dns_records']["txt"]:
                temp_txt.append(_.replace('"', r'\"'))
            
            result['dns_records']["txt"] = temp_txt
        if session.get("instance_id") and result:
            footprint_save_to_db("Passive", "dnsdumpster", f"'Domain': '{domain}'", False, json.dumps(result),
                                 session["instance_id"])
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

    if session.get("instance_id") and result:
        footprint_save_to_db("Passive", "geoip", f"'IP': '{ip}', 'Method': '{name}'", False, json.dumps(result),
                             session["instance_id"])
    return jsonify(result)


@app.route('/_googledork', methods=['GET', 'POST'])
def googledork():
    domain = request.args.get('domainName')
    dork = request.args.get('dork')
    google_dork_obj = GoogleDork(domain)
    result = google_dork_obj.single_query(dork)

    if session.get("instance_id") and result:
        footprint_save_to_db("Passive", "googledork", f"'Domain': '{domain}', 'Dork': '{dork}'", True,
                             json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_reverseip/<name>', methods=['GET', 'POST'])
def reverseip(name=None):
    ip = request.args.get('ip')
    reverseip_obj = ReverseIPLookup(ip)
    if name == "yougetsignal":
        result = reverseip_obj.query_yougetsignal()
    elif name == "Hackertarget":
        result = reverseip_obj.query_hackertarget()

    if session.get("instance_id") and result:
        footprint_save_to_db("Passive", "reverseip", f"'IP': '{ip}', 'Method': '{name}'", True, json.dumps(result),
                             session["instance_id"])
    return jsonify(result)


@app.route('/_subdomain/<name>', methods=['GET', 'POST'])
def subdomain(name=None):
    domain = request.args.get('domainName')
    subdomain_obj = Subdomain(domain)
    if name == "google_dork":
        result = subdomain_obj.google()
    elif name == "dnsdumpster":
        result = subdomain_obj.dnsdumpster()

    if session.get("instance_id") and result:
        footprint_save_to_db("Passive", "subdomain", f"'Domain': '{domain}', 'Method': '{name}'", True,
                             json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_wayback', methods=['GET', 'POST'])
def wayback():
    domain = request.args.get('domainName')
    start_year = request.args.get('startYear')
    stop_year = request.args.get('stopYear')
    wayback_obj = WayBackMachine(domain)
    result = wayback_obj.get_urls(start_year, stop_year)

    if session.get("instance_id") and result:
        footprint_save_to_db("Passive", "wayback", f"'Domain': '{domain}'", True, json.dumps(result),
                             session["instance_id"])
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

    if session.get("instance_id") and result:
        footprint_save_to_db("Passive", "whois", f"'Domain': '{domain}', 'IP': '{ip}', 'Method': '{name}'", True,
                             json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/footprinting/active/<name>', methods=['GET', 'POST'])
def active(name=None):
    global active_modules_list
    module_details = active_modules_list["active"][name]

    if session.get("instance_id"):
        if session["instance_id"]:
            flash(session["instance_name"] + " is active instance. All the results will be saved to database.")

    if name == "buildwith":
        return render_template('_buildwith.html', title='Footprinting', details=module_details)

    elif name == "robot":
        return render_template('_robot.html', title='Footprinting', details=module_details)

    elif name == "sslinfo":
        return render_template('_sslinfo.html', title='Footprinting', details=module_details)

    elif name == "traceroute":
        return render_template('_traceroute.html', title='Footprinting', details=module_details)

    elif name == "osmapping":
        return render_template('_osmapping.html', title='Footprinting', details=module_details)

    elif name == "webserver":
        return render_template('_webserverdetect.html', title='Footprinting', details=module_details)

    return render_template('footprinting.html')


@app.route('/_buildwith', methods=['GET', 'POST'])
def buildwith():
    domain = request.args.get('domainName')
    https = request.args.get('https')
    buildwith_obj = BuildWith(domain, https)
    result = buildwith_obj.discover()

    if session.get("instance_id") and result:
        footprint_save_to_db("Active", "buildwith", f"'Domain': '{domain}', 'HTTPS': '{https}'",
                             False, json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_robot/<name>', methods=['GET', 'POST'])
def robot(name=None):
    domain = request.args.get('domainName')
    https = request.args.get('https')
    robot_obj = Robot_sitemap(domain, https)
    if name == "robot":
        result = robot_obj.robot()
    elif name == "sitemap":
        result = robot_obj.sitemap()

    if session.get("instance_id") and result:
        footprint_save_to_db("Active", "robot", f"'Domain': '{domain}', 'HTTPS': '{https}', 'Method': '{name}'", True,
                             json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_sslinfo', methods=['GET', 'POST'])
def sslinfo():
    domain = request.args.get('domainName')
    https = request.args.get('https')
    ssl_obj = SSL(domain, https)
    result = ssl_obj.get_ssl()

    if session.get("instance_id") and result:
        footprint_save_to_db("Active", "sslinfo", f"'Domain': '{domain}', 'HTTPS': '{https}'", True,
                             json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_traceroute', methods=['GET', 'POST'])
def traceroute():
    ip = request.args.get('ip')
    https = request.args.get('https')
    source = request.args.get('source')
    traceroute_obj = Traceroute(ip, https, source)
    result = traceroute_obj.traceroute()

    if session.get("instance_id") and result:
        footprint_save_to_db("Active", "traceroute", f"'IP': '{ip}', 'HTTPS': '{https}'", True, json.dumps(result),
                             session["instance_id"])
    return jsonify(result)


@app.route('/_osmapping', methods=['GET', 'POST'])
def osmapping():
    ip = request.args.get('ip')
    nmap_obj = Nmap_auto()
    result = nmap_obj.osmap(ip)
    if 'error' not in result.keys():
        if session.get("instance_id") and result:
            footprint_save_to_db("Active", "osmapping", f"'IP': '{ip}'", True, json.dumps(result),
                                 session["instance_id"])
    return jsonify(result)


@app.route('/_webserver', methods=['GET', 'POST'])
def webserver():
    domain = request.args.get('domainName')
    https = request.args.get('https')
    webserver_obj = Webserver_detect(https, domain)
    result = webserver_obj.detect()
    print(result)
    if session.get("instance_id") and result:
        footprint_save_to_db("Active", "webserver", f"'Domain': '{domain}'", False, json.dumps(result),
                             session["instance_id"])
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


@app.route('/enumeration', methods=['GET', 'POST'])
def enumeration():
    global enumeration_modules_list
    return render_template('enumeration.html', title='Enumeration',
                           enumeration_list=enumeration_modules_list["enumeration"])


@app.route('/enumeration/modules/<name>', methods=['GET', 'POST'])
def enumeration_modules(name=None):
    global enumeration_modules_list
    module_details = enumeration_modules_list["enumeration"][name]

    if session.get("instance_id"):
        if session["instance_id"]:
            flash(session["instance_name"] + " is active instance. All the results will be saved to database.")

    if name == "subnet":
        return render_template('_subnet.html', title='Enumeration', details=module_details)

    elif name == "portscan":
        return render_template('_portscan.html', title='Enumeration', details=module_details)

    elif name == "dnsbrute":
        return render_template('_dnsbrute.html', title='Enumeration', details=module_details)

    elif name == "pingscan":
        return render_template('_pingscan.html', title='Enumeration', details=module_details)

    return render_template('enumeration.html', title='Enumeration', enumeration_list=enumeration_modules_list)


@app.route('/_dnsbrute', methods=['GET', 'POST'])
def dnsbrute():
    domain = request.args.get('domainName')
    nmap_obj = Nmap_auto()
    result = nmap_obj.dnsbrute(domain)
    if session.get("instance_id"):
        footprint_save_to_db("Enumeration", "dnsbrute", f"'Domain': '{domain}'", True,
                             json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_subnet', methods=['GET', 'POST'])
def subnet():
    ip = request.args.get('ip')
    nmap_obj = Nmap_auto()
    result = nmap_obj.subnet(ip)
    if 'error' not in result.keys():
        if session.get("instance_id"):
            footprint_save_to_db("Enumeration", "subnet", f"'IP': '{ip}'", True,
                                 json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_portscan', methods=['GET', 'POST'])
def portscan():
    ip = request.args.get('ip')
    nmap_obj = Nmap_auto()
    result = nmap_obj.topports(ip)
    if 'error' not in result.keys():
        if session.get("instance_id"):
            footprint_save_to_db("Enumeration", "portscan", f"'IP': '{ip}'", True,
                                 json.dumps(result), session["instance_id"])
    return jsonify(result)


@app.route('/_pingscan', methods=['GET', 'POST'])
def pingscan():
    ip = request.args.get('ip')
    nmap_obj = Nmap_auto()
    result = nmap_obj.pingscan(ip)
    if 'error' not in result.keys():
        if session.get("instance_id"):
            footprint_save_to_db("Enumeration", "pingscan", f"'IP': '{ip}'", True,
                                 json.dumps(result), session["instance_id"])
    return jsonify(result)


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
