# Batch Rename
import os
# Function to rename multiple files
i = 1
dirname = os.getcwd()
dirname = dirname + r"\renameme"
print(dirname)

for filename in os.listdir(dirname):
    end = filename[8:]
    end = end[1:]
    endnum = int(end[:-4])
    endnum = endnum + 11600
    dst = filename[0:7] + "0_" + str(endnum) + ".tif"
    src = dirname + "\\" + filename
    dst = dirname + "\\" + dst
    print(filename)
    print(dst)
    # rename() function will
    # rename all the files
    os.rename(src, dst)
    i += 1
