#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        init
# Purpose:     For package
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from raven.gui.forms import InstanceForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JvuxmTfG8bYjVPrN7hfMVi9QcLdl2lF8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raven.db'
db = SQLAlchemy(app)

from raven.gui import routes
