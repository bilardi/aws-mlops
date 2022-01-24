#!/usr/bin/env bash

# check if there is environment variable named AWS_PROFILE
if [ -z $AWS_PROFILE ]; then
    echo
    echo Environment variable AWS_PROFILE not exists
    echo Usage: AWS_PROFILE=development bash $0
    echo
    exit 1
fi

# initialization
STAGE='studio'
AWS_REGION="eu-west-1"
path=$(dirname $0)
cd $path

# unit tests
echo Unit tests
cd ..
python3 -m unittest discover -v
cd -

# functional tests of processing steps and 
echo Functional tests
#AWS_PROFILE=$AWS_PROFILE AWS_REGION=$AWS_REGION bash test_docker.sh auto

AWS_PROFILE=$AWS_PROFILE AWS_REGION=$AWS_REGION bash test_docker.sh pretraining > pretraining.log
export KEY=$(grep "KEY:" pretraining.log | awk '{print $2}')
AWS_PROFILE=$AWS_PROFILE AWS_REGION=$AWS_REGION bash test_docker.sh testing

AWS_PROFILE=$AWS_PROFILE AWS_REGION=$AWS_REGION bash test_docker.sh preinference > preinference.log
export KEY=$(grep "KEY:" preinference.log | awk '{print $2}')
AWS_PROFILE=$AWS_PROFILE AWS_REGION=$AWS_REGION bash test_docker.sh reporting

# infrastructure validation
cd ..
echo Infrastructure validation
STAGE=$STAGE AWS_REGION=$AWS_REGION bash deploy.sh test
