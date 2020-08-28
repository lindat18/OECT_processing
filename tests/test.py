import os
import sys
import pytest
import configparser
import numpy as np
sys.path.insert(0,'..')

import oect
test_oect = oect.OECT(folder='test_device/no_config')