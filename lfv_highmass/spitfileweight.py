import sys
import os 
for filename in os.listdir(sys.argv[1]):
    if "lumicalc.sum" in filename and "data" not in filename and "DY" not in filename:
        with open(sys.argv[1]+"/"+filename) as lumifile:
            lumistr=float(lumifile.readline().strip())

        print filename,":  ",lumistr,"    ",1/lumistr
