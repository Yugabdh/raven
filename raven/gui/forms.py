#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        forms
# Purpose:     Creating forms with validation
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class InstanceForm(FlaskForm):
    instance_name = StringField('Instance Name', validators=[DataRequired()])
    domain = StringField('Domain Name', validators=[DataRequired()])
    note = StringField('Note', widget=TextArea())
    https = BooleanField('HTTPS')
    submit = SubmitField('Create')


class APIKeyForm(FlaskForm):
    ipstack = StringField('ipstack API key')
    ipinfo = StringField('ipinfo API key')
    whatcms = StringField('whatcms API key')
    submit = SubmitField('Update')


class CMSForm(FlaskForm):
    domain = StringField('Domain Name', validators=[DataRequired()])
    submit = SubmitField('Discover')


class DNSDumpsterForm(FlaskForm):
    domain = StringField('Domain Name', validators=[DataRequired()])
    submit = SubmitField('Dive')


class GeoIPLookupForm(FlaskForm):
    ip = StringField('IP address', validators=[DataRequired()])
    submit = SubmitField('Locate')


class GoogleDorkForm(FlaskForm):
    dork = StringField('Dork string', validators=[DataRequired()])
    submit = SubmitField('Fire')


class ReverseIPLookupForm(FlaskForm):
    ip = StringField('IP address', validators=[DataRequired()])
    submit = SubmitField('Lookup')


class WayBackMachineForm(FlaskForm):
    domain = StringField('Domain Name', validators=[DataRequired()])
    start_year = IntegerField('Results Starting From Year', validators=[DataRequired()])
    end_year = IntegerField('Results ending From Year')
    submit = SubmitField('Time Travel')


class WhoislookupForm(FlaskForm):
    domain = StringField('Domain Name', validators=[DataRequired()])
    ip = StringField('IP address', validators=[DataRequired()])
    submit = SubmitField('Lookup')
