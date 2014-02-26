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


"""CloudSim dashboard module."""

__author__ = 'ammp'

import time
import webapp2
import os
import datetime
import sys

from common import safe_dom
from common import tags
from controllers import utils
from controllers import cloudsim_utils
from models import custom_modules

from cloudsim_rest_api import CloudSimRestApi


class CloudsimTestLaunchHandler(utils.BaseHandler):
    """Handler for launch page."""

    def get(self):
        """Handles GET requests."""
        status = ""
        alert = ""
        self.template_value['navbar'] = {}
        self.template_value['status'] = status
        self.render('cloudlaunch.html')

    def post(self):
        """Handles POST requests."""

        def _get_now_str(days_offset=0):
                """
                Returns a utc string date time format of now, with optional
                offset.
                """
                dt = datetime.timedelta(days=days_offset)
                now = datetime.datetime.utcnow()
                t = now - dt
                s = t.isoformat()
                return s
        
        status = "Connect to a Simulator to view tasks"
        alert = ""

        action = self.request.get("action", '')

        ip_address = self.request.get('ip_address')
        username = self.request.get('username')
        password = self.request.get('password')
        simulator_name = self.request.get('simulator_name')

        task_title = self.request.get('task_title')
        ros_package = self.request.get('ros_package')
        launch_filename = self.request.get('launch_filename')
        bash_filename = self.request.get('bash_filename')

        task_dict = {}
        task_dict['task_title'] = task_title
        task_dict['ros_package'] = ros_package
        task_dict['ros_launch'] = launch_filename
        task_dict['launch_args'] = ''
        task_dict['timeout'] = '3600'
        task_dict['latency'] = '0'
        task_dict['uplink_data_cap'] = '0'
        task_dict['downlink_data_cap'] = '0'
        task_dict['local_start'] = _get_now_str(-1)
        task_dict['local_stop'] = _get_now_str(1)
        task_dict['bash_src'] =  bash_filename  
        task_dict['vrc_id'] = 1
        task_dict['vrc_num'] = 1

        if action == "checkstatus":
            try:
                cloudsim_api = CloudSimRestApi(ip_address, username, password) 
                status = str(cloudsim_api.get_tasks(simulator_name))
            except:
                e = sys.exc_info()[0]
                print(e)
                alert = "An error occured while connecting to the simulator; " + str(e)
        
        elif action == "launchtask":
            try:
                cloudsim_api = CloudSimRestApi(ip_address, username, password)
                task_id = cloudsim_api.create_task(simulator_name, task_dict)
                cloudsim_api.start_task(simulator_name, task_id)
            except:
                e = sys.exc_info()[0]
                print(e)
                alert = "An error occured while launching task; " + str(e)
            

        self.template_value['navbar'] = {}
        self.template_value['status'] = status
        self.template_value['alert'] = alert
        self.render('cloudlaunch.html')
        

# Coursebuilder
def register_module():
    """Registers this module in the registry."""

    # register custom tag
    #tags.Registry.add_tag_binding('cloudsim', CloudsimTag)

    # register handlers
    # zip_handler = ('/khan-exercises', sites.make_zip_handler(ZIP_FILE))
    # render_handler = ('/khan-exercises/khan-exercises/indirect/', KhanExerciseRenderer)
    launch_handler = ('/cloudlaunch', CloudsimTestLaunchHandler)

    # register module
    global custom_module
    custom_module = custom_modules.Module(
        'Cloudsim Test',
        'A set of pages for starting/stopping Cloudsim machines via '
        'Course Builder.',
        [], [launch_handler])
    return custom_module        
