#!pip install GitPython
#!pip install sagemaker
#!pip install s3fs
#!pip install aws-mlops
import os
import sys
#import config as config
import definitions as definitions
sys.path.insert(1, os.getcwd() + '/..')
from aws_mlops.mlops import MLOps

# initialization
mo = MLOps(definitions)

# create definition files
mo.create_step_functions_definition_files()
