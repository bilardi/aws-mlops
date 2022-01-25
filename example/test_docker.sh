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

# main
path=$(dirname $0)
cd $path

account_id=$(aws sts get-caller-identity | grep Account | awk '{print $2}' | sed 's/[",]//g')
repository="$account_id.dkr.ecr.$AWS_REGION.amazonaws.com/mlops-$STAGE-processing"
if [ -d '/codebuild' ]; then
    commit=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | head -c 8) # for CD
else
    commit=$(git rev-parse HEAD | head -c 8) # for testing
fi
processing_repository_uri="$repository:$commit"
echo "ECR repo: $processing_repository_uri"

echo "get arguments of $processing processing:"
arguments=$(python -c "import config as config; print(config.${processing}_input['arguments'])" | sed "s/[,'\[\]]*//g")
echo $arguments
key=$(echo $arguments | awk '{print $NF}')
echo "KEY: $key"

if [ "$processing" == "testing" ] || [ "$processing" == "reporting" ]; then
    previous_processing='pretraining'
    if [ "$processing" == "reporting"  ]; then
        previous_processing='preinference'
    fi
    cp processing/test_data/test.$previous_processing.csv processing/test_data/test.csv
    cp processing/prediction/test.csv.$previous_processing.out processing/prediction/test.csv.out
fi

echo "docker build"
docker build -t $processing_repository_uri .

echo "docker run"
if [ $(docker ps -a | grep -c -w testprocessing) -ne 0 ]; then
    docker stop testprocessing
    docker rm testprocessing
fi
volume=""
if [ "$processing" == "preinference" ]; then
    volume="-v $PWD/processing/new_data:/opt/ml/processing/input"
fi

docker run --name testprocessing -e AWS_PROFILE=$AWS_PROFILE -v $HOME/.aws/credentials:/root/.aws/credentials:ro $volume $processing_repository_uri $arguments
cd -

if [ "$processing" == "pretraining" ] || [ "$processing" == "preinference" ]; then
    if [ "$processing" == "pretraining" ]; then
        docker cp testprocessing:/opt/ml/processing/train/train.csv processing/train_data/
        docker cp testprocessing:/opt/ml/processing/validation/validation.csv processing/validation_data/
    fi
    docker cp testprocessing:/opt/ml/processing/test/test.csv processing/test_data/
    aws s3 cp s3://sagemaker-$AWS_REGION-$account_id/$key/testing_data/ processing/testing_data/ --recursive
    echo processing/train_data/train.csv
    diff processing/train_data/train.csv processing/train_data/train.$processing.csv
    echo processing/validation_data/validation.csv
    diff processing/validation_data/validation.csv processing/validation_data/validation.$processing.csv
    echo processing/test_data/test.csv
    diff processing/test_data/test.csv processing/test_data/test.$processing.csv
    echo processing/testing_data/id.csv
    diff processing/testing_data/id.csv processing/testing_data/id.$processing.csv
    echo processing/testing_data/columns_names.csv
    diff processing/testing_data/columns_names.csv processing/testing_data/columns_names.$processing.csv
    echo processing/testing_data/quality.csv
    diff processing/testing_data/quality.csv processing/testing_data/quality.$processing.csv
else
    docker cp testprocessing:/opt/ml/processing/prediction/prediction.csv processing/prediction/
    docker cp testprocessing:/opt/ml/processing/report/report.csv processing/report/
    echo processing/prediction/prediction.csv
    diff processing/prediction/prediction.csv processing/prediction/prediction.$processing.csv
    echo processing/report/report.csv
    diff processing/report/report.csv processing/report/report.$processing.csv
fi
