import os 
import sys
for filename in os.listdir(sys.argv[1]):
    if "weight" in filename and "data" not in filename:
        with open(sys.argv[1]+"/"+filename) as lumifile:
            lumistr=float(lumifile.readline().strip().replace("Weights: ",""))

        print filename,":  ",lumistr,"    "
