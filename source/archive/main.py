#!/usr/bin/env python3

import os

from usrConst import *

print('=' * 10)

print(BASE_PATH)
print(PATH_GIF, PATH_PHOTO, PATH_VIDEO, PATH_VOICE, PATH_OTHER)

print('=' * 10)


print(os.path.realpath(PATH_GIF))

