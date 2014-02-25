This is a robotics courseware prototype that runs on the following:

- (GAE) Google AppEngine 1.8.8 
- (GCB) course-builder 1.5.1

Additional Files/Folders:

- modules/cloudsim_dash
- views/testlaunch.html

Running Development Server in Linux (assumes Python 2.7 is installed, Tested on Ubuntu 12.04.3):

1. Download and extract GAE App Engine SDK for python (v1.8.8). Location with extracted files will be /GAEPATH (http://googleappengine.googlecode.com/files/google_appengine_1.8.8.zip)
2. Include GAEPATH/ to environment $PATH
3. Clone/Download and extract cloudsim-ed-web. Extracted location will be your APP_PATH/ (https://bitbucket.org/ammpedro/cloudsim-ed-web)
4. To run the GAE development server, change directory to APPATH/ and run command: dev_appserver.py .
5. Explore APP_PATH/ sample code or Browse http://localhost:8080 

Full instructions here: https://code.google.com/p/course-builder/wiki/CourseBuilderChecklist

To Deploy (sunlit-vortex-447.appspot.com via cloudsim.ed@gmail.com)

1. cd APP_PATH/
2. appcfg.py update .
