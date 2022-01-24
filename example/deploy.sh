#!/usr/bin/env bash

action=$1

# check if there is environment variable named STAGE
if [ -z ${STAGE} ]; then
    echo
    echo Environment variable STAGE not exists
    echo Usage: STAGE=development bash $0 [test]
    echo Example for deploying: STAGE=development AWS_REGION=eu-west-1 bash $0
    echo Example for testing: STAGE=development AWS_REGION=eu-west-1 bash $0 test 
    echo
    exit 1
fi

# initialization
if [ -z $AWS_REGION ]; then
    AWS_REGION="eu-west-1"
fi
if [ -z $action ]; then
    action='deploy'
    mode=''
else
    action='print'
    mode='test'
fi

# main
path=$(dirname $0)
cd $path

echo "create step functions definitions"
pip install --upgrade -r requirements.txt
python3 create_definitions.py
cp $STAGE.pretraining.definition.json ../default.processing.definition.json
cp $STAGE.modeling.definition.json ../default.modeling.definition.json
cp $STAGE.prediction.definition.json ../default.prediction.definition.json
cp $STAGE.mlops.definition.json ../default.mlops.definition.json
cd -

echo "remove building files"
make clean

echo "deploy infrastructure"
SLS_DEBUG=* sls $action --stage $STAGE

echo "build new image"
cd $path
bash build_image.sh $mode
cd -
