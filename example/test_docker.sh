#!/usr/bin/env bash

processing=$1

# check if there is environment variable named AWS_PROFILE
if [ -z $AWS_PROFILE ] || [ -z $processing ]; then
    echo
    echo Environment variable AWS_PROFILE not exists or missing processing_name
    echo Usage: AWS_PROFILE=development bash $0 processing_name
    echo Example: AWS_PROFILE=development AWS_REGION=eu-west-1 bash $0 pretraining
    echo
    exit 1
fi

# initialization
if [ -z $AWS_REGION ]; then
    AWS_REGION="eu-west-1"
fi

account_id=$(aws sts get-caller-identity | grep Account | awk '{print $2}' | sed 's/[",]//g')
repository="$account_id.dkr.ecr.$AWS_REGION.amazonaws.com/mlops-$STAGE-processing"
commit=$(git rev-parse HEAD | head -c 8)
processing_repository_uri="$repository:$commit"
echo "ECR repo: $processing_repository_uri"

# main
path=$(dirname $0)
cd $path

echo "get arguments of $processing processing:"
arguments=$(python -c "import config as config; print(config.${processing}_input['arguments'])" | sed "s/[,'\[\]]*//g")
echo $arguments

echo "docker build"
docker build -t $processing_repository_uri .

echo "docker run"
docker run -e AWS_PROFILE=$AWS_PROFILE -v $HOME/.aws/credentials:/root/.aws/credentials:ro $processing_repository_uri $arguments
cd -
