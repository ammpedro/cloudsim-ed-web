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

import cgi
import urllib
import json 

from common import safe_dom
from common import tags
from controllers import utils
from controllers.utils import BaseHandler
from controllers import cloudsim_utils
from models import custom_modules

from models import models
from models import utils
from models import transforms
from models.config import ConfigProperty
from models.config import ConfigPropertyEntity
from models.courses import Course
from models.models import Student
from models.models import StudentProfileDAO
from models.models import TransientStudent
from models.models import StudentAnswersEntity
from models.roles import Roles

from tools import verify

from controllers import assessments

from google.appengine.ext import db

from cloudsim_rest_api import CloudSimRestApi

class CloudsimAssessmentHandler(BaseHandler):
    """Handles simulation launches."""

    @db.transactional(xg=True)
    def update_simassessment_transaction(
        self, email, assessment_type, new_answers, score):
        """Stores answer and updates user scores.

        Args:
            email: the student's email address.
            assessment_type: the title of the assessment.
            new_answers: the latest set of answers supplied by the student.
            score: the numerical assessment score.

        Returns:
            the student instance.
        """
        student = Student.get_enrolled_student_by_email(email)
        print student.is_transient
        course = self.get_course()

        # It may be that old Student entities don't have user_id set; fix it.
        if not student.user_id:
            student.user_id = self.get_user().user_id()

        answers = StudentAnswersEntity.get_by_key_name(student.user_id)
        if not answers:
            answers = StudentAnswersEntity(key_name=student.user_id)
        answers.updated_on = datetime.datetime.now()

        utils.set_answer(answers, assessment_type, new_answers)

        assessments.store_score(course, student, assessment_type, int(score))

        student.put()
        answers.put()   

    def post(self):
        """Handles POST requests"""

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
        alert = ''
        student = self.personalize_page_and_get_enrolled()
        if not student:
            print "not student"
            self.redirect('/course#registration_required')
            return

        def wait_for_task_state(cloudsim_api,
                                constellation_name,
                                task_id,
                                target_state,
                                max_count=100,
                                sleep_secs=1):
            """
            Wait until the task is in a target state (ex "running", or "stopped")
            """
            count = 0
            while True:
                time.sleep(sleep_secs)
                count += 1
                if count > max_count:
                    raise RestException("Timeout in start_task"
                                        "%s for %s" % (task_id, constellation_name))    
                task_dict = cloudsim_api.read_task(constellation_name, task_id)
                current_state = task_dict['task_state']
                print("%s/%s Task %s: %s" % (count, max_count,
                                             task_id,
                                             current_state))
                if current_state == target_state:
                    return

        #if not self.assert_xsrf_token_or_fail(self.request, 'assessment-post'):
        #    return

        course = self.get_course()
        assessment_name = self.request.get('name')
        if not assessment_name:
            self.error(404)
            print 'No assessment type supplied.'
            return

        unit = course.find_unit_by_id(assessment_name)
        if unit is None or unit.type != verify.UNIT_TYPE_ASSESSMENT:
            self.error(404)
            print ('No assessment named %s exists.', assessment_name)
            return

        self.template_value['cloudsim_ip'] = student.cloudsim_ip
        self.template_value['cloudsim_uname'] = student.cloudsim_uname
        self.template_value['cloudsim_passwd'] = student.cloudsim_passwd
        self.template_value['cloudsim_simname'] = student.cloudsim_simname

        action = self.request.get('action')
        print action
        if action == "launch":
            try:
                task_dict = {}
                task_dict['task_title'] = 'Cloudsim-Ed_' + assessment_name
                task_dict['ros_package'] = 'cloudsim_ed_actuation'
                print assessment_name
                if assessment_name == "Lab1":
                    task_dict['ros_launch'] = 'cloudsim_ed_actuation_challenge_01.launch'
                    ipynb_name = "Actuation_Challenge_01"
                elif assessment_name == "Lab2":
                    task_dict['ros_launch'] = 'cloudsim_ed_perception_challenge_01.launch'
                    ipynb_name = "Perception_Challenge_01"
                elif assessment_name == "Lab3":
                    task_dict['ros_launch'] = 'cloudsim_ed_navigation_challenge_01.launch'
                    ipynb_name = "Navigation_Challenge_01"

                task_dict['launch_args'] = ''
                task_dict['timeout'] = '3600'
                task_dict['latency'] = '0'
                task_dict['uplink_data_cap'] = '0'
                task_dict['downlink_data_cap'] = '0'
                task_dict['local_start'] = _get_now_str(-1)
                task_dict['local_stop'] = _get_now_str(1)
                task_dict['bash_src'] = '/home/ubuntu/cloudsim-ed-actuation/src/cloudsim-ed-actuation/setup.bash'  
                task_dict['vrc_id'] = 1
                task_dict['vrc_num'] = 1

                # create and start cloudsim task
                cloudsim_api = CloudSimRestApi(student.cloudsim_ip, student.cloudsim_uname, student.cloudsim_passwd) 
                cloudsim_api.create_task(student.cloudsim_simname, task_dict)
                print "Task Created"
                task_list = cloudsim_api.get_tasks(student.cloudsim_simname)
                for task in task_list:
                    if (task['task_message'] == 'Ready to run') and (task['task_title'] == task_dict['task_title']):          
                        cloudsim_api.start_task(student.cloudsim_simname, task['task_id'])
                        wait_for_task_state(cloudsim_api,
                                            student.cloudsim_simname,
                                            task['task_id'],
                                            'running',
                                            max_count,
                                            sleep_secs)

                # start gzweb
                cloudsim_api.start_gzweb(student.cloudsim_simname)
                # start ipython notebook
                cloudsim_api.start_notebook(student.cloudsim_simname)
                simulator_data = cloudsim_api.get_constellation_data(student.cloudsim_simname)
                gzweb_url = 'http://' + simulator_data['sim_public_ip'] + ':8080'

                ipynb_id = ''
                data = urllib2.urlopen(simulator_data["http://"+'sim_public_ip']+":8888/notebooks") 
                json_data=data.read()
                list_o_dicts=json.loads(json_data)
                for d in list_o_dicts:
                    if d['name'] == ipynb_name: 
                        ipynb_id = d['notebook_id']

                ipynb_url = 'http://' + simulator_data['sim_public_ip'] + ':8888/' + ipynb_id

                splitscreen_url = "http://" + student.cloudsim_ip + "/cloudsim/inside/cgi-bin/splitsim?sim_ip=" + simulator_data['sim_public_ip'] +"&notebook_id=" + ipynb_id

                goto_url = "/assessment?name=" + assessment_name
                
                self.template_value['challenge_name'] = assessment_name
                self.template_value['gzweb'] = gzweb_url
                self.template_value['ipynb'] = ipynb_url
                self.template_value['splitscn'] = splitscreen_url
                self.render(challenge.html)    

            except:
                e = sys.exc_info()[0]
                print(e)
                alert = "An error occured while starting the challenge. Are your CloudSim credentials working?" + str(e)
                self.template_value['navbar'] = {}
                self.template_value['alert'] = alert
                self.render('/cloudlaunch.html')

        elif action == "reset":
            print name
    
        elif action == "getscore":
            try:
                msg = ''
                score = 0
                student = self.personalize_page_and_get_enrolled()
                cloudsim_api = CloudSimRestApi(student.cloudsim_ip, student.cloudsim_uname, student.cloudsim_passwd)
                task_list = cloudsim_api.get_tasks(student.cloudsim_simname)
                for task in task_list:
                    if task['task_state'] == 'running':
                        s = str(task['task_message'])

                if s:
                    task_msg = dict(zip(s.splitlines()[0].split(','), s.splitlines()[1].split(',')))
                else:
                    return

                course = self.get_course()
                answers = ''
                
                if assessment_name == "Lab1":
                    score = int(float(task_msg['field.completion_score'])/2) * 100
                elif assessment_name == "Lab2":
                    score = int(task_msg['field.completion_score']) * 10
                elif assessment_name == "Lab3":
                    score = int(task_msg['field.completion_score']) * 10
                else:
                    score = int(task_msg['field.completion_score']) * 10

                # Record assessment transaction.
                assessment_transaction = self.update_simassessment_transaction(
                    student.key().name(), assessment_name, answers, int(score))
                # FIXME later: mark assessment as completed
                course.get_progress_tracker().put_assessment_completed(student, assessment_name)

                # stop stuff
                cloudsim_api.stop_gzweb(student.cloudsim_simname)
                cloudsim_api.stop_notebook(student.cloudsim_simname)
                cloudsim_api.stop_task(student.cloudsim_simname)

                self.template_value['navbar'] = {}
                self.template_value['score'] = score

                # for the actuation challenge
                if assessment_name == "Lab1":
                    self.template_value['assessment_name'] = 'Actuation Challenge'

                # for the perception challenge
                elif assessment_name == "Lab2":
                    self.template_value['assessment_name'] = 'Perception Challenge'

                # for the navigation challenge
                elif assessment_name == "Lab3":
                    self.template_value['assessment_name'] = 'Navigation Challenge'

                # for a simulation assessment that has a a nice name hopefully
                else:                
                    self.template_value['assessment_name'] = assessment_name

                self.render('test_confirmation.html')

            except:
                e = sys.exc_info()[0]
                print(e)
                alert = "An error occured while getting your score. Are you connected to a Simulation?" + str(e)
                self.template_value['navbar'] = {}
                self.template_value['alert'] = alert
                self.render('/cloudlaunch.html')

        
class CloudsimCredentialsEditHandler(BaseHandler):
    """Handles edits to student cloudsim credentials."""

    def post(self):
        """Handles POST requests."""
        student = self.personalize_page_and_get_enrolled()
        if not student:
            print "not student"
            self.redirect('/course#registration_required')
            return

        if not self.assert_xsrf_token_or_fail(self.request, 'student-edit'):
            print "token fail"            
            return

        Student.edit_cloudsim_credentials(self.request.get('cloudsim_ip'), 
                            self.request.get('cloudsim_uname'), self.request.get('cloudsim_passwd'),
                            self.request.get('cloudsim_simname'))
        
        self.redirect('/student/home')

class CloudsimTestLaunchHandler(BaseHandler):
    """Handler for launch page."""

    def get(self):
        """Handles GET requests."""
        status = "Connect to a simulator to view available tasks"
        alert = ""
        task_list = ""

        student = self.personalize_page_and_get_enrolled()
        if not student:
            self.redirect('/course#registration_required')
            return

        name = student.name
        profile = student.profile
        if profile:
            name = profile.nick_name

        self.template_value['cloudsim_ip'] = student.cloudsim_ip
        self.template_value['cloudsim_uname'] = student.cloudsim_uname
        self.template_value['cloudsim_passwd'] = student.cloudsim_passwd
        self.template_value['cloudsim_simname'] = student.cloudsim_simname

        try:
            cloudsim_api = CloudSimRestApi(student.cloudsim_ip, student.cloudsim_uname, student.cloudsim_passwd) 
            task_list = cloudsim_api.get_tasks(student.cloudsim_simname)
            sim_data = cloudsim_api.get_constellation_data(student.cloudsim_simname)
            status = "Getting Sim Data Here"

        except:
            e = sys.exc_info()[0]
            print(e)
            alert = "An error occured while connecting to the simulator. Are you sure your credentials are updated? " + str(e)
            self.template_value['navbar'] = {}
            self.template_value['alert'] = alert
            self.template_value['status'] = "An Error Occured."
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
        
        status = ""
        alert = ""
        task_list = ""

        student = self.personalize_page_and_get_enrolled()
        if not student:
            return

        name = student.name
        profile = student.profile
        if profile:
            name = profile.nick_name

        action = self.request.get("action", '')
 
        if action == "checkstatus":
            try:
                cloudsim_api = CloudSimRestApi(student.cloudsim_ip, student.cloudsim_uname, student.cloudsim_passwd) 
                task_list = cloudsim_api.get_tasks(student.cloudsim_simname)
                status = ""

            except:
                e = sys.exc_info()[0]
                print(e)
                alert = "An error occured while connecting to the simulator; " + str(e)
                status = "An Error Occured."

        elif action == "createtask":
            try:
                student = self.personalize_page_and_get_enrolled()
                if not student:
                    alert = "Please Register to view simulations."
                    self.redirect('/course#registration_required')
                    return

                course = self.get_course()
                name = student.name
                profile = student.profile
                if profile:
                    name = profile.nick_name
               
                task_name = self.request.get('task_name')

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

                cloudsim_api = CloudSimRestApi(student.cloudsim_ip, student.cloudsim_uname, student.cloudsim_passwd)
                task_id = cloudsim_api.create_task(student.cloudsim_simname, task_dict)
                task_list = cloudsim_api.get_tasks(student.cloudsim_simname)
                status = ""
                alert = "Task Created"
            except:
                e = sys.exc_info()[0]
                print(e)
                alert = "An error occured while launching task; " + str(e)
                status = "An Error Occured."


        self.template_value['navbar'] = {}
        self.template_value['status'] = status
        self.template_value['alert'] = alert
        self.template_value['task_list'] = task_list

        self.template_value['cloudsim_ip'] = student.cloudsim_ip
        self.template_value['cloudsim_uname'] = student.cloudsim_uname
        self.template_value['cloudsim_passwd'] = student.cloudsim_passwd
        self.template_value['cloudsim_simname'] = student.cloudsim_simname

        self.render('cloudlaunch.html')
        

# Coursebuilder
def register_module():
    """Registers this module in the registry."""

    # register custom tag
    #tags.Registry.add_tag_binding('cloudsim', CloudsimTag)

    # register handlers
    # zip_handler = ('/khan-exercises', sites.make_zip_handler(ZIP_FILE))
    credentials_handler = ('/cloudlaunch/edit', CloudsimCredentialsEditHandler)
    launch_handler = ('/cloudlaunch', CloudsimTestLaunchHandler)
    assessment_handler = ('/cloudlaunch/assess', CloudsimAssessmentHandler)

    # register module
    global custom_module
    custom_module = custom_modules.Module(
        'Cloudsim Test',
        'A set of pages for starting/stopping Cloudsim machines via '
        'Course Builder.',
        [], [launch_handler, credentials_handler, assessment_handler])
    return custom_module        

