# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Classes and methods to create and manage Announcements."""

__author__ = '(cloudsim.ed@gmail.com)'


import datetime
import urllib

from common import tags
from controllers.utils import BaseHandler
from controllers.utils import BaseRESTHandler
from controllers.utils import ReflectiveRequestHandler
from controllers.utils import XsrfTokenManager
from models import custom_modules
from models import entities
from models import notify
from models import roles
from models import transforms
from models.models import MemcacheManager
from models.models import Student
import modules.announcements.samples as samples
from modules.oeditor import oeditor

from google.appengine.ext import db




def register_module():
    """Registers this module in the registry."""

    # register custom tag
    #tags.Registry.add_tag_binding('cloudsimlaunch', CloudSimLaunchTag)

    # register handlers
    #zip_handler = (
    #    '/khan-exercises', sites.make_zip_handler(ZIP_FILE))
    #launch_handler = ('/cloudsim/', CloudSimLaunchRenderer)

    # register module
    global custom_module
    custom_module = custom_modules.Module(
        'Launch CloudSim Simulation Task',
        'A set of pages for delivering CloudSim Environments via '
        'Course Builder.',
        [], [])
    return custom_module    
