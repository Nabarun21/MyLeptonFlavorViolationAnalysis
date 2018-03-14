import sys
import os 
import subprocess
for filename in os.listdir(sys.argv[1]+"/"+sys.argv[2]):
    if "JetsToLL" in filename and "DY" in filename:
	newfilename=filename.split("ToLL",1)[0]+filename.split("JetsToLL",1)[1]
	newfilename=newfilename.replace("DY","ZTauTau")
	command="cp "+sys.argv[1]+"/"+sys.argv[2]+"/"+filename+" "+sys.argv[1]+"/"+sys.argv[2]+"/"+newfilename
	print command
	print ""
	subprocess.call(command.split())
