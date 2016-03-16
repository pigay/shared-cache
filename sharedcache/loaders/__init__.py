from loader import *
from httploader import *
from md5decorator import *
from tarfiledecorator import *

try:
  from diracloader import *
except ImportError:
  pass
