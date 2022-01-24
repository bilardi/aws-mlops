import os
import sys
import subprocess
# import boto3 # for SSM
import argparse
import importlib
from git import Repo

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-url', type=str, default='https://github.com/bilardi/aws-mlops.git')
    parser.add_argument('--repo-name', type=str, default='aws-mlops')
    parser.add_argument('--repo-branch', type=str, default='alessandra')
    parser.add_argument('--config-path', type=str, default='example.config')
    parser.add_argument('--config-item', type=str, default='pretraining_input')
    parser.add_argument('--class-path', type=str, default='example.prep_with_pandas')
    parser.add_argument('--class-name', type=str, default='PrepWithPandas')
    parser.add_argument('--key', type=str, default='')
    # parser.add_argument('--git-username', type=str, default='/git/username')
    # parser.add_argument('--git-password', type=str, default='/git/token')
    args, _ = parser.parse_known_args()
    print('Received arguments {}'.format(args))

    # # get region name for SSM
    # region_name='eu-west-1'
    # if os.environ.get('AWS_REGION'):
    #    region_name = os.environ.get('AWS_REGION')
    # boto3.setup_default_session(region_name=region_name)

    # # get git token from SSM for a private repository
    # ssm = boto3.client('ssm')
    # username = ssm.get_parameter(Name=args.git_username)
    # password = ssm.get_parameter(Name=args.git_password, WithDecryption=True)
    # repo_url = args.repo_url.format(username['Parameter']['Value'], password['Parameter']['Value'])

    # installation
    if os.path.isdir(args.repo_name):
        subprocess.run(["rm", "-rf", args.repo_name], capture_output=True)
    repo = Repo.clone_from(args.repo_url, args.repo_name, multi_options=[f'-b {args.repo_branch}'])
    os.chdir(args.repo_name)
    sys.path.insert(0, '')
    os.environ['KEY'] = args.key

    # import config and class files
    config = importlib.import_module(args.config_path)
    class_module = importlib.import_module(args.class_path)
    proc_class = getattr(class_module, args.class_name)
    proc_obj = proc_class()

    # running the class method imported
    feedback = proc_obj.run(args.config_item, config)

    print('Received feedback from {}: {}'.format(args.class_name, feedback))
    
