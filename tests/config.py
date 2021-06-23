import os.path
import git
from datetime import datetime
from sagemaker.tuner import IntegerParameter, ContinuousParameter

# methods
def get_commit():
    repo = git.Repo(search_parent_directories=True)
    return repo.head.object.hexsha
def create_ts():
    now = datetime.now()
    return now.strftime("%Y-%m-%d-%H-%M-%S")
def slash_to_dash(string):
    return string.replace('/','-')

# simple input
environment='studio'
application='aws-mlops'
branch='main'
commit=get_commit()
ts = create_ts()
key=f'{application}/{branch}/{commit}/{ts}'

# complex input
estimator_input = {
    'environment':environment,
    'application':application,
    'container':{
        'framework':'xgboost',
        'version':'latest'
    }
}
tuner_input = {
    'environment':environment,
    'application':application,
    'base_tuning_job_name':slash_to_dash(key),
    'hyperparameter_ranges':{
        'alpha':ContinuousParameter(1,2),
        'num_round':IntegerParameter(500,1500)
    }
}
