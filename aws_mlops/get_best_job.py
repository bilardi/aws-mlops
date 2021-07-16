"""Methods for getting training job details

The methods are loaded on a lambda and the handler is:
    aws_mlops/get_best_job.main

# license MIT
# author Alessandra Bilardi <alessandra.bilardi@gmail.com>
# see https://github.com/bilardi/aws-mlops for details
"""
import boto3
sm = boto3.client('sagemaker')

def describe_training_job(job_name):
    """
    gets the training job details
        Arguments:
            job_name (str): training job name
        Returns:
            dictionary with HyperParameter and S3ModelArtifacts
    """
    job_description = sm.describe_training_job(TrainingJobName=job_name)
    return {
        'HyperParameter': job_description['HyperParameters'],
        'S3ModelArtifacts': job_description['ModelArtifacts']['S3ModelArtifacts']
    }

def main(event, context):
    """
    gets the training job details
        Arguments:
            event (dict): with TrainingJobName parameter
        Returns:
            dictionary with statusCode and body
    """
    details = describe_training_job(event['TrainingJobName'])
    payload = {
        'statusCode': 200,
        'body': details
    }
    payload['body'].update(event)
    return payload