import os
import git
from pathlib import Path
import json
from datetime import datetime

import boto3
import sagemaker
region_name='eu-west-1'
if os.environ.get('AWS_REGION'):
    region_name = os.environ.get('AWS_REGION')
if os.path.isdir('/Users') or os.path.isdir('/home/jovyan/'):
    profile_name='your-account'
    if os.environ.get('AWS_PROFILE'):
        profile_name = os.environ.get('AWS_PROFILE')
    boto3.setup_default_session(profile_name=profile_name, region_name=region_name)
else:
    boto3.setup_default_session(region_name=region_name)

def get_git_details(main_branch):
    try:
        repo = git.Repo(search_parent_directories=True)
        return [ repo.active_branch.name, repo.head.object.hexsha ]
    except:
        return [ main_branch, 'hash_fake' ]

def create_ts():
    now = datetime.now()
    return now.strftime('%Y-%m-%d-%H-%M-%S')
def slash_to_dash(string):
    return string.replace('/','-')
def point_to_dash(string):
    return string.replace('.','-')
def dictionary_from_module(module):
    context = {}
    black_list = ['os', 'git', 'Path', 'json', 'datetime', 'boto3', 'sagemaker', 'get_git_details', 'create_ts', 'slash_to_dash', 'point_to_dash', 'dictionary_from_module', 'load_file', 'load_queries']
    for setting in dir(module):
        # you can write your filter here
        if not setting.startswith('_') and not setting in (black_list):
            context[setting] = getattr(module, setting)
    return context
def load_file(filename):
    response = None
    if Path(filename).is_file():
        with open(filename) as json_file:
            response = json.load(json_file)
    return response
def load_queries(files):
    inputs = []
    for file in files:
        input = None
        if Path(file).is_file():
            # for make input
            input = load_file(file)
        else:
            # for jupyter
            file = '../' + file
            input = load_file(file)
        inputs.append(input)
    return inputs

# common input
service = 'mlops' # name of your service
environment = 'studio' # for CD: stanging / production
main_branch = 'master'
if os.environ.get('STAGE'):
    environment = os.environ.get('STAGE')
[ branch, commit ] = get_git_details(main_branch)
repo_url = 'https://github.com/bilardi/aws-mlops.git'
repo_name = 'aws-mlops'
#branch = 'alessandra'
#commit = 'bc7ed76e07967efaf3993b437a2d65b3ce28e19c'
ecr_repository_name = f'{service}-{environment}-processing'
ts = create_ts()

# environment details of Step Functions execution
execution_id = ''
#execution_id = 'arn:aws:states:eu-west-1:1234567890:execution:mlops-studio-prediction:mlops-studio-prediction-2021-07-14T15-58-52193906'
if os.environ.get('ExecutionId'):
    execution_id = os.environ.get('ExecutionId')
execution_name = ''
#execution_name = 'mlops-studio-prediction-2021-07-14T15-58-52193906'
if os.environ.get('ExecutionName'):
    execution_name = os.environ.get('ExecutionName')

source_bucket = sagemaker.Session().default_bucket() # for testing
if branch == main_branch and environment == 'production':
    source_bucket = 'your-bucket' # for CD
model_bucket = source_bucket # it is different, if you want to define an expiration date for old models
destination_bucket = source_bucket # it is different, if you want to define a trigger for your predictions / reports
key = f'{repo_name}/{branch}/{commit}/{ts}' # for testing
if branch == main_branch:
    key=f'{repo_name}/{branch}/{environment}/{commit}/{ts}' # for CD
if os.environ.get('KEY'):
    key = os.environ.get('KEY')

# you can define statically some parameters here
#key='mlops/alessandra/4c25c805c46c2d2865c2eab995fa968a61c0eaf6/2021-10-18-10-24-38'
#BestTrainingJob = {'TrainingJobName': 'mlopsstudio20210714T09235703702-008-5e5c0ba9'}
#model_input_id='mlopsstudio20210714t09235703702'
#role_arn=''
#processing_image_uri=''
#container_image_uri=''

# key-dependent variables
dash_key = slash_to_dash(key)
test_key = key # it is different, if you want to try modeling without to run again pretraining
execution_ssm=f'/{key.replace(repo_name, service)}/execution-details'
#execution_ssm=f'/{key}/execution-details' # No access to reserved parameter name (with prefix aws-)

# you can define statically some parameters here
#test_key='mlops/alessandra/bc7ed76e07967efaf3993b437a2d65b3ce28e19c/2021-07-14-09-23-20'

# path of your data
raw_data_filename='winequality-red.csv'
raw_data_key=f'{repo_name}/{branch}/raw_data' # for testing
if branch == main_branch:
    raw_data_filename='data.csv'
    raw_data_key=f'{key}/raw_data' # for CD
raw_data_s3_url=f's3://{source_bucket}/{raw_data_key}/{raw_data_filename}'

new_data_filename='winequality-white.csv'
new_data_key=f'{repo_name}/{branch}/new_data' # for testing
if branch == main_branch:
    new_data_filename='data.csv'
    new_data_key=f'{key}/new_data' # for CD
new_data_path=f's3://{source_bucket}/{new_data_key}'
new_data_s3_url=f'{new_data_path}/{new_data_filename}'

target='quality'
identifier='id'
score='score'
test_size=0.3
validation_size=0.2

test_filename='test.csv'
test_data_key=f'{test_key}/test_data'
testing_data_key=f'{test_key}/testing_data'
test_path=f's3://{source_bucket}/{test_data_key}'
test_s3_url=f'{test_path}/{test_filename}'

train_filename='train.csv'
train_path=f's3://{source_bucket}/{test_key}/train_data'
train_s3_url=f'{train_path}/{train_filename}'

validation_filename='validation.csv'
validation_data_key=f'{test_key}/validation_data'
validation_path=f's3://{source_bucket}/{validation_data_key}'
validation_s3_url=f'{validation_path}/{validation_filename}'

models_path=f's3://{model_bucket}/{key}/models'
models_ssm=f'/{service}/{repo_name}/{branch}/model-input-id'
#models_ssm=f'/{repo_name}/{branch}/model-input-id' # No access to reserved parameter name (with prefix aws-)

#score_filename='.csv.out'
score_path=f's3://{source_bucket}/{key}/prediction'
#score_s3_url=f'{score_path}/{score_filename}'

prediction_filename='prediction.csv'
# prediction_path=score_path
prediction_path=f's3://{destination_bucket}/{key}/prediction'
report_filename='report.csv'
report_path=f's3://{destination_bucket}/{key}/report'

# input for images and containers
container_input = {
    'framework':'xgboost',
    'version':'latest',
    'InstanceCount': 1,
    'InstanceType': 'ml.m5.large',
    'VolumeSizeInGB': 10
}

processing_input = {
    'InstanceCount': 1,
    'InstanceType': 'ml.t3.large',
    'VolumeSizeInGB': 10
}

# input for processing
auto_input = {
    'arguments': [
        '--repo-url', repo_url,
        '--repo-name', repo_name,
        '--repo-branch', branch,
        '--config-path', 'example.config',
        '--config-item', 'auto_input',
        '--class-path', 'example.auto_with_pandas',
        '--class-name', 'AutoWithPandas',
        '--key', key
    ],
    'inputs': [
        {
            'InputName': raw_data_filename,
            'S3Input': {
                'LocalPath': '/opt/ml/processing/input',
                'S3Uri': raw_data_s3_url,
                'S3InputMode': 'File',
                'S3DataType': 'S3Prefix'
            }
        }
    ],
    'outputs': [
        {
            'OutputName': train_filename,
            'S3Output': { 
                'LocalPath': '/opt/ml/processing/train',
                'S3Uri': train_path,
                'S3UploadMode': 'EndOfJob'
            }
        },
        {
            'OutputName': test_filename,
            'S3Output': { 
                'LocalPath': '/opt/ml/processing/test',
                'S3Uri': test_path,
                'S3UploadMode': 'EndOfJob'
            }
        }        
    ]
}
pretraining_input = {
    'arguments': [
        '--repo-url', repo_url,
        '--repo-name', repo_name,
        '--repo-branch', branch,
        '--config-path', 'example.config',
        '--config-item', 'pretraining_input',
        '--class-path', 'example.prep_with_pandas',
        '--class-name', 'PrepWithPandas',
        '--key', key
    ],
    'inputs': [
        {
            'InputName': raw_data_filename,
            'S3Input': {
                'LocalPath': '/opt/ml/processing/input',
                'S3Uri': raw_data_s3_url,
                'S3InputMode': 'File',
                'S3DataType': 'S3Prefix'
            }
        }
    ],
    'outputs': [
        {
            'OutputName': train_filename,
            'S3Output': { 
                'LocalPath': '/opt/ml/processing/train',
                'S3Uri': train_path,
                'S3UploadMode': 'EndOfJob'
            }
        },
        {
            'OutputName': validation_filename,
            'S3Output': { 
                'LocalPath': '/opt/ml/processing/validation',
                'S3Uri': validation_path,
                'S3UploadMode': 'EndOfJob'
            }
        },
        {
            'OutputName': test_filename,
            'S3Output': { 
                'LocalPath': '/opt/ml/processing/test',
                'S3Uri': test_path,
                'S3UploadMode': 'EndOfJob'
            }
        }
    ]
}
preinference_input = {
    'arguments': [
        '--repo-url', repo_url,
        '--repo-name', repo_name,
        '--repo-branch', branch,
        '--config-path', 'example.config',
        '--config-item', 'preinference_input',
        '--class-path', 'example.prep_with_pandas',
        '--class-name', 'PrepWithPandas',
        '--key', key
    ],
    'inputs': [
        {
            'InputName': new_data_filename,
            'S3Input': {
                'LocalPath': '/opt/ml/processing/input',
                'S3Uri': new_data_s3_url,
                'S3InputMode': 'File',
                'S3DataType': 'S3Prefix'
            }
        }
    ],
    'outputs': [
        {
            'OutputName': test_filename,
            'S3Output': {
                'LocalPath': '/opt/ml/processing/test',
                'S3Uri': test_path,
                'S3UploadMode': 'EndOfJob'
            }
        }
    ]
}

# input for modeling
tuning_input = {
    'max_runtime_in_seconds': 86400,
    'static_hyper_parameters': {
        '_kfold': '5',
        '_num_cv_round': '3',
        'gamma': '1.6816270262197224e-06',
        'lambda': '0.009173719287637053',
        'min_child_weight': '0.006254071319537053',
        'objective': 'reg:linear',
        'subsample': '0.6058771210998253',
        'eval_metric':'rmse'
    },
    'hyper_parameter_tuning': {
        'Strategy': 'Bayesian',
        'ResourceLimits': {
            'MaxNumberOfTrainingJobs': 10, #250,
            'MaxParallelTrainingJobs': 10
        },
        'TrainingJobEarlyStoppingType': 'Auto',
        'HyperParameterTuningJobObjective': {
            'Type': 'Minimize',
            'MetricName': 'validation:rmse'
        },
        'ParameterRanges': {
            'ContinuousParameterRanges': [
                {
                    'Name': 'eta',
                    'MinValue': '0.02',
                    'MaxValue': '0.04',
                    'ScalingType': 'Auto'
                },
                {
                    'Name': 'colsample_bytree',
                    'MinValue': '0.5',
                    'MaxValue': '0.8',
                    'ScalingType': 'Auto'
                },
                {
                    'Name': 'alpha',
                    'MinValue': '1',
                    'MaxValue': '3',
                    'ScalingType': 'Auto'
                }
            ],
            'CategoricalParameterRanges': [],
            'IntegerParameterRanges': [
                {
                    'Name': 'num_round',
                    'MinValue': '400',
                    'MaxValue': '800',
                    'ScalingType': 'Auto'
                },
                {
                    'Name': 'max_depth',
                    'MinValue': '2',
                    'MaxValue': '10',
                    'ScalingType': 'Auto'
                }
            ]
        }
    }
}
training_input = {
    'static_hyper_parameters': {
        '_kfold': '5',
        '_num_cv_round': '3',
        'alpha': '2.519849147096237e-05',
        'colsample_bytree': '0.6509641408101212',
        'eta': '0.02903202312960693',
        'gamma': '1.6816270262197224e-06',
        'lambda': '0.009173719287637053',
        'max_depth': '2',
        'min_child_weight': '0.006254071319537053',
        'num_round': '597',
        # 'reg:linear', 'reg:logistic', 'binary:logistic', 'binary:logitraw', 'count:poisson', 'multi:softmax', 'multi:softprob', 'rank:pairwise', 'reg:gamma', 'reg:tweedie'
        'objective': 'reg:linear',
        'subsample': '0.6058771210998253',
        'eval_metric':'rmse'
    }
}

# input for reporting
testing_input = {
    'arguments': [
        '--repo-url', repo_url,
        '--repo-name', repo_name,
        '--repo-branch', branch,
        '--config-path', 'example.config',
        '--config-item', 'testing_input',
        '--class-path', 'example.test_with_pandas',
        '--class-name', 'TestWithPandas',
        '--key', key
    ],
    'inputs': [
        {
            'InputName': test_filename + '.out',
            'S3Input': {
                'LocalPath': '/opt/ml/processing/score',
                'S3Uri': score_path,
                'S3InputMode': 'File',
                'S3DataType': 'S3Prefix'
            }
        },
        {
            'InputName': test_filename,
            'S3Input': {
                'LocalPath': '/opt/ml/processing/test',
                'S3Uri': test_s3_url,
                'S3InputMode': 'File',
                'S3DataType': 'S3Prefix'
            }
        }
    ],
    'outputs': [
        {
            'OutputName': prediction_filename,
            'S3Output': {
                'LocalPath': '/opt/ml/processing/prediction',
                'S3Uri': prediction_path,
                'S3UploadMode': 'EndOfJob'
            }
        },
        {
            'OutputName': report_filename,
            'S3Output': {
                'LocalPath': '/opt/ml/processing/report',
                'S3Uri': report_path,
                'S3UploadMode': 'EndOfJob'
            }
        }
    ]
}
reporting_input = {
    'arguments': [
        '--repo-url', repo_url,
        '--repo-name', repo_name,
        '--repo-branch', branch,
        '--config-path', 'example.config',
        '--config-item', 'reporting_input',
        '--class-path', 'example.test_with_pandas',
        '--class-name', 'TestWithPandas',
        '--key', key
    ],
    'inputs': [
        {
            'InputName': test_filename + '.out',
            'S3Input': {
                'LocalPath': '/opt/ml/processing/score',
                'S3Uri': score_path,
                'S3InputMode': 'File',
                'S3DataType': 'S3Prefix'
            }
        }
    ],
    'outputs': [
        {
            'OutputName': prediction_filename,
            'S3Output': {
                'LocalPath': '/opt/ml/processing/prediction',
                'S3Uri': prediction_path,
                'S3UploadMode': 'EndOfJob'
            }
        },
        {
            'OutputName': report_filename,
            'S3Output': {
                'LocalPath': '/opt/ml/processing/report',
                'S3Uri': report_path,
                'S3UploadMode': 'EndOfJob'
            }
        }
    ]
}
