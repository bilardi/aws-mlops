import os
import sys
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
    args, _ = parser.parse_known_args()
    print('Received arguments {}'.format(args))

    # installation
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
    