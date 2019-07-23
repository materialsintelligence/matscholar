#!/usr/bin/env python
# coding: utf-8
# Copyright (c) Matscholar Development Team.
# Distributed under the terms of the MIT License.

import os
import sys
import shutil
from monty.serialization import loadfn, dumpfn

from matscholar import SETTINGS_FILE


def add_config_var(args):
    d = {}
    if os.path.exists(SETTINGS_FILE):
        shutil.copy(SETTINGS_FILE, SETTINGS_FILE + ".bak")
        print("Existing %s backed up to %s"
              % (SETTINGS_FILE, SETTINGS_FILE + ".bak"))
        d = loadfn(SETTINGS_FILE)
    toks = args.var_spec
    if len(toks) % 2 != 0:
        print("Bad variable specification!")
        sys.exit(-1)
    for i in range(int(len(toks) / 2)):
        d[toks[2 * i]] = toks[2 * i + 1]
    dumpfn(d, SETTINGS_FILE, default_flow_style=False)
    print("New %s written!" % (SETTINGS_FILE))


def set_config(config):
    if os.path.exists(SETTINGS_FILE):
        shutil.copy(SETTINGS_FILE, SETTINGS_FILE + ".bak")
        print("Existing %s backed up to %s"
              % (SETTINGS_FILE, SETTINGS_FILE + ".bak"))
    dumpfn(config, SETTINGS_FILE, default_flow_style=False)
    print("New %s written!" % (SETTINGS_FILE))


def configure_mscli(args):
    if args.var_spec:
        add_config_var(args)
