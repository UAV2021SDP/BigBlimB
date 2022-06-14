# University of California, Santa Cruz - UAV Airship Capstone 
Atharva Ranadive, Ahmed Alazzawi, Danielle Laganiere, and Will Daschbach


### Project Description
With many bodies of water in remote and hard to reach locations, sending a hydrologist out to conduct water quality assessments can be difficult and time consuming. A UAV payload can be designed with a multiparameter water quality probe (aka “sonde”) to reach these remote bodies of water much easier than a hydrologist on foot can and collect useful data from a wide range of points along the water’s surface. Using an airship to improve energy consumption during hovering, an autonomous flight and water sampling system could be implemented to allow for improved efficiency and decreased human error. 


### Code Overview and Organization
Within this repo, the subsystems are clearly marked within folders, each containing the relevant files. The Embedded System files call files from the other folders in order to complete the various protocols. Included, each folder contains various testing files and examples the group has created throughout the project to help them test and conclude functionality.

The main file which will be run in order to run the Payload Protocols is the TopLevelHSM.py file, which calls all of the other neccassary files. This will eventually be the start up file when the pi is turned on, although at this point the project is not far enough into the testing state for this to happen. All files are written in Python 3, except the Ardupilot which acts as a firmware to the Pixhawk 4.


To pull repo with vehicle code use: 
  git pull --recurse-submodules
OR 
  git pull
  git submodule update --init
