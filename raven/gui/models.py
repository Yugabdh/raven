#!/usr/bin/env python3

# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# Name:        models
# Purpose:     SQLAlchemy classes for entities
#
# Author:      Yugabdh Pashte <yugabdhppashte.com>
# ------------------------------------------------------------------------------

from datetime import datetime

from raven.gui import db


class Instance(db.Model):
    __tablename__ = 'instance'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    domain = db.Column(db.String(60), unique=False, nullable=False)
    https = db.Column(db.Boolean, unique=False, default=True)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    footprints = db.relationship('Footprint', backref='target', lazy=True)


class Footprint(db.Model):
    __tablename__ = 'footprint'
    id = db.Column(db.Integer, primary_key=True)
    type_recon = db.Column(db.String(20), nullable=False)
    module_name = db.Column(db.String(60), nullable=False)
    params_value = db.Column(db.String(100), nullable=False)
    overflow = db.Column(db.Boolean, unique=False, default=True)
    scan_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    result = db.Column(db.Text, nullable=False)
    instance_id = db.Column(db.Integer, db.ForeignKey('instance.id'), nullable=False)


db.create_all()
