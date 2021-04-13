#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        forms
# Purpose:     Creating forms with validation
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
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
