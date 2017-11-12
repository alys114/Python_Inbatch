# Author: Vincent.chan
# Blog: http://blog.alys114.com

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE_DIR)

from core import in_batch

if __name__ == '__main__':
	in_batch.main()