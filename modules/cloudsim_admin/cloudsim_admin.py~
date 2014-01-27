# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
from __future__ import print_function

"""Cloudsim admin module."""

__author__ = 'ammp'

from common import safe_dom
from common import tags
from controllers import utils
from models import custom_modules

# cloudsim 1.7.3
import os
import sys
import unittest
import time
import datetime
import logging

from cloudsim_rest_api import CloudSimRestApi
import traceback

# add cloudsim directory to sytem path
basepath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, basepath)
print (sys.path)

import cloudsimd.launchers.cloudsim as cloudsim
from cloudsimd.launchers.launch_utils.launch_db import ConstellationState
from cloudsimd.launchers.launch_utils.launch_db import get_unique_short_name
from cloudsimd.launchers.launch_utils.testing import get_test_runner
from cloudsimd.launchers.launch_utils.testing import get_boto_path
from cloudsimd.launchers.launch_utils.testing import get_test_path


CLOUDSIM_CONFIG = "CloudSim-stable"
SIM_CONFIG = "Simulator-stable"

try:
    logging.basicConfig(filename='/tmp/rest_integration_test.log',
                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                level=logging.DEBUG)
except Exception, e:
    print("Can't enable logging: %s" % e)




def register_module():
    """Registers this module in the registry."""

    # register custom tag
    #tags.Registry.add_tag_binding('cloudsim', CloudsimTag)

    # register handlers
    # zip_handler = ('/khan-exercises', sites.make_zip_handler(ZIP_FILE))
    # render_handler = ('/khan-exercises/khan-exercises/indirect/', KhanExerciseRenderer)

    # register module
    global custom_module
    custom_module = custom_modules.Module(
        'Cloudsim Test',
        'A set of pages for starting/stopping Cloudsim machines via '
        'Course Builder.',
        [], [])
    return custom_module        
