#!/usr/bin/env bash

action=$1

# check if there is environment variable named STAGE
if [ -z ${STAGE} ]; then
    echo
    echo Environment variable STAGE not exists
    echo Usage: STAGE=development bash $0 [test]
    echo Example for pushing: STAGE=development AWS_REGION=eu-west-1 bash $0
    echo Example for testing: STAGE=development AWS_REGION=eu-west-1 bash $0 test
    echo
    exit 1
fi

# initialization
if [ -z $AWS_REGION ]; then
    AWS_REGION="eu-west-1"
fi
if [ -z $action ]; then
    action='push'
fi

account_id=$(aws sts get-caller-identity | grep Account | awk '{print $2}' | sed 's/[",]//g')
repository="$account_id.dkr.ecr.$AWS_REGION.amazonaws.com/mlops-$STAGE-processing"
commit=$(git rev-parse HEAD | head -c 8)
processing_repository_uri="$repository:$commit"
echo "ECR repo: $processing_repository_uri"

# main
path=$(dirname $0)
cd $path

echo "docker build"
docker build -t $processing_repository_uri .

if [ $action == 'push' ]; then
    echo "get login"
    if [ $(aws --version | awk '{print $1}' | awk -F'/' '{print $2}' | awk -F'.' '{print $1}') -eq 1 ]; then
        # AWS CLI version 1
        $(aws ecr get-login --region $AWS_REGION --no-include-email)
    else
        # AWS CLI version 2
        aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $repository
    fi
    echo "docker push"
    docker push $processing_repository_uri
fi

cd -
