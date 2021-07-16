"""Methods for managing the states inputs

The methods are loaded on a lambda and the handler is:
    aws_mlops/config_manager.main

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-mlops for details
"""
import boto3
import json
from botocore.exceptions import ClientError
ssm = boto3.client('ssm')
s3 = boto3.client('s3')
sfn = boto3.client('stepfunctions')

def get_config_by_ssm(parameter_name):
    """
    gets the configuration saved on ssm
        Arguments:
            parameter_name (str): name of execution of state machine
        Returns:
            dictionary of config
    """
    try:
        details = ssm.get_parameter(Name=parameter_name)
    except ClientError:
        return {}
    return json.loads(details['Parameter']['Value'])

def save_config_by_ssm(parameter_name, value):
    """
    saves the configuration merged with the last OutputPath
        Arguments:
            parameter_name (str): name of execution of state machine
            value (dict): dictionary of the configuration
    """
    result = ssm.put_parameter(Name=parameter_name, Value=json.dumps(value), Type='String', Overwrite=True)
    if result['Version'] >= 1:
        return
    raise ValueError(value)

def remove_config_by_ssm(parameter_name):
    """
    removes the configuration on ssm
        Arguments:
            parameter_name (str): name of execution of state machine
    """
    result = ssm.delete_parameter(Name=parameter_name)
    if 'ResponseMetadata' in result and 'HTTPStatusCode' in result['ResponseMetadata'] and result['ResponseMetadata']['HTTPStatusCode'] == 200:
        return
    raise ValueError(result)

def get_config_by_s3(bucket, key):
    """
    gets the configuration saved on s3
        Arguments:
            bucket (str): name of bucket
            key (str): path and filename
        Returns:
            dictionary of config
    """
    try:
        details = s3.get_object(Bucket=bucket, Key=key)
    except ClientError:
        return {}
    return json.loads(details['Body'].read())

def save_config_by_s3(bucket, key, value):
    """
    saves the configuration merged with the last OutputPath
        Arguments:
            bucket (str): name of bucket
            key (str): path and filename
            value (dict): dictionary of the configuration
    """
    result = s3.put_object(
        ACL='bucket-owner-full-control',
        Body=json.dumps(value).encode('ascii'), #b''
        Bucket=bucket,
        Key=key
    )
    if 'VersionId' in result and isinstance('VersionId', str):
        return

def remove_config_by_s3(bucket, key):
    """
    removes the configuration on s3
        Arguments:
            bucket (str): name of bucket
            key (str): path and filename
    """
    result = s3.delete_object(Bucket=bucket, Key=key)
    if 'VersionId' in result and isinstance('VersionId', str):
        return

def get_config_by_sfn(execution_arn):
    """
    gets the configuration passed at the start the state machine
        Arguments:
            execution_arn (str): ARN of execution of state machine 
        Returns:
            dictionary of config
    """
    execution_details = sfn.describe_execution(executionArn=execution_arn)
    return json.loads(execution_details['input'])

def main(event, context = None):
    """
    manages the states inputs
        Arguments:
            event (dict): with ExecutionName parameter [and last_output with other all parameters]
        Returns:
            dictionary with statusCode and body
    """
    key = event['ExecutionName'].replace('-','/',3)
    parameter_name = '/' + key
    if 'source_bucket' in event['last_output']:
        bucket = event['last_output']['source_bucket']
    else:
        bucket = get_config_by_ssm(parameter_name)
    payload = get_config_by_s3(bucket, key)
    if not payload:
        payload = get_config_by_sfn(event['ExecutionId'])
    payload.update(event['last_output'])
    save_config_by_ssm(parameter_name, bucket)
    save_config_by_s3(bucket, key, payload)
    if event['StateName'] == 'GoToEnd':
        remove_config_by_ssm(parameter_name)
#        remove_config_by_s3(bucket, key)
    return {
        'statusCode': 200,
        'body': payload
    }
