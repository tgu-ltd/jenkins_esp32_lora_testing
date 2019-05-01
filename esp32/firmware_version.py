import os

with open('./firmware_version.txt', 'w') as f:
    f.write(str(os.uname()))
