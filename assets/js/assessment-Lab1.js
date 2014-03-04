// Copyright 2012 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


// When the assessment page loads, activity-generic.js will render the contents
// of the 'assessment' variable into the enclosing HTML webpage.

// For information on modifying this page, see
// https://code.google.com/p/course-builder/wiki/CreateAssessments.


var assessment = {
  // HTML to display at the start of the page
  preamble: '<h1>Actuation Challenge</h1>\
             <form method="post" action="/cloudlaunch/assess?action=launch&name=Lab1">\
             <button class="gcb-button" type="submit">Launch Task</button> &nbsp;&nbsp;&nbsp\
             <button class="gcb-button" type="submit" formaction="/cloudlaunch/assess?action=reset&name=Lab1">Reset Task</button> &nbsp;&nbsp;&nbsp \
             <button class="gcb-button" type="submit" formaction="/cloudlaunch/assess?action=getscore&name=Lab1">End Task</button></form>',

  // An ordered list of questions, with each question's type implicitly determined by the fields it possesses:
  //   choices              - multiple choice question (with exactly one correct answer)
  //   correctAnswerString  - case-insensitive string match
  //   correctAnswerRegex   - freetext regular expression match
  //   correctAnswerNumeric - freetext numeric match
  questionsList: [
    
    //{questionHTML: 'What would you type into the search box to get a top result that looks like this? If you do not know, enter "I don\'t know".<p><p><img src="assets/img/Image0.9.png" alt="search results for test question" height=100 width=300 title="search results for test question">',
    // correctAnswerRegex: /354\s*[+]\s*651/
    //}
  ],

  // The assessmentName key is deprecated in v1.3 of Course Builder, and no
  // longer used. The assessment name should be set in the unit.csv file or via
  // the course editor interface.
  assessmentName: 'Lab1', // unique name submitted along with all of the answers

  checkAnswers: false,    // render a "Check your Answers" button to allow students to check answers prior to submitting?

  exam_assessment: false
}
