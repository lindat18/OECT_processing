import os
import sys
import pytest
import configparser
import numpy as np
sys.path.insert(0,'..')

import oect
test_oect = oect.OECT(folder='test_device/01')
test_oect.filelist()
print(os.path.join('test_device/01', 'uc1_kpf6_output_0.txt') in test_oect.files
	and os.path.join('test_device/01', 'uc1_kpf6_output_1.txt') in test_oect.files
	and os.path.join('test_device/01', 'uc1_kpf6_transfer_0.txt') in test_oect.files
	and test_oect.config[0] == os.path.join('test_device/01', 'uc1_kpf6_config.cfg'))
print(test_oect.config[0])