#!python3

import os

# get list of folders in 'plug-ins' directory

# change cwd to plug-ins
os.chdir("plug-ins")

for dir in os.listdir("."):
    plug_in = os.path.join(dir, f"{dir}.py")

    if not os.path.isdir(dir) or not os.path.exists(plug_in):
        continue

    print(plug_in)

    # new_dir = dir.replace("-", "_")
    # new_plug_in = os.path.join(dir, f"{new_dir}.py")
    # # new_dir_path = os.path.join("plug-ins", dir.replace("-", "_"))
    # os.rename(plug_in, new_plug_in)
    # os.rename(dir, new_dir)


    # print(new_plug_in)
