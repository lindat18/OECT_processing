import os
import sys
import pytest
import configparser
import numpy as np
sys.path.insert(0,'..')

import oect
with pytest.raises(FileNotFoundError):
	oect.make_config('a_nonexistent_path')