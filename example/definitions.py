import config as config
service = config.service
environment = config.environment

import os
if os.environ.get('STAGE'):
    environment = os.environ.get('STAGE')

# input for preprocessing
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html
pretraining_input = {
    'AppSpecification': {
        'ImageUri.$': '$.processing_image_uri',
        'ContainerArguments.$': '$.pretraining_input.arguments',
        'ContainerEntrypoint': [ 'python3', '/app/processing.py' ]
    },
    'Environment': {
#        'last_output.$': '$',
        'ExecutionId.$': '$$.Execution.Id',
        'ExecutionName.$': '$$.Execution.Name'
    },
    'ProcessingResources': {
        'ClusterConfig': {
            'InstanceCount.$': "$.processing_input['InstanceCount']",
            'InstanceType.$': "$.processing_input['InstanceType']",
            'VolumeSizeInGB.$': "$.processing_input['VolumeSizeInGB']"
        }
    },
    'ProcessingInputs.$': '$.pretraining_input.inputs',
    'ProcessingOutputConfig': {
        'Outputs.$': '$.pretraining_input.outputs'
    },
    'RoleArn.$': '$.role_arn',
    'ProcessingJobName.$': '$.pretraining_input_id'
}
preinference_input = {
    'AppSpecification': {
        'ImageUri.$': '$.processing_image_uri',
        'ContainerArguments.$': '$.preinference_input.arguments',
        'ContainerEntrypoint': [ 'python3', '/app/processing.py' ]
    },
    'Environment': {
#        'last_output.$': '$',
        'ExecutionId.$': '$$.Execution.Id',
        'ExecutionName.$': '$$.Execution.Name'
    },
    'ProcessingResources': {
        'ClusterConfig': {
            'InstanceCount.$': "$.processing_input['InstanceCount']",
            'InstanceType.$': "$.processing_input['InstanceType']",
            'VolumeSizeInGB.$': "$.processing_input['VolumeSizeInGB']"
        }
    },
    'ProcessingInputs.$': '$.preinference_input.inputs',
    'ProcessingOutputConfig': {
        'Outputs.$': '$.preinference_input.outputs'
    },
    'RoleArn.$': '$.role_arn',
    'ProcessingJobName.$': '$.preinference_input_id'
}

# input for modeling
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateHyperParameterTuningJob.html
tuning_input = {
    'TrainingJobDefinition': {
        'AlgorithmSpecification': {
            'TrainingImage.$': '$.container_image_uri',
            'TrainingInputMode': 'File'
        },
        'OutputDataConfig': {
            'S3OutputPath.$': '$.models_path'
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds.$': '$.tuning_input.max_runtime_in_seconds'
        },
        'ResourceConfig': {
            'InstanceCount.$': "$.container_input['InstanceCount']",
            'InstanceType.$': "$.container_input['InstanceType']",
            'VolumeSizeInGB.$': "$.container_input['VolumeSizeInGB']"
        },
        'RoleArn.$': '$.role_arn',
        'InputDataConfig': [
            {
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri.$': '$.train_path',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'text/csv',
                'ChannelName': 'train'
            },
            {
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri.$': '$.validation_path',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'text/csv',
                'ChannelName': 'validation'
            }
        ],
        'StaticHyperParameters.$': '$.tuning_input.static_hyper_parameters'
    },
    'HyperParameterTuningJobName.$': '$.tuner_input_id',
    'HyperParameterTuningJobConfig.$': '$.tuning_input.hyper_parameter_tuning' 
}
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html
training_input = {}

# input for inference
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModel.html
model_input = {
    'ExecutionRoleArn.$': '$.role_arn',
    'ModelName.$': '$.model_input_id',
    'PrimaryContainer': {
        'Environment': {},
        'Image.$': '$.container_image_uri',
        'ModelDataUrl.$': "$['S3ModelArtifacts']"
    }
}
# # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html
# endpoint_config_input = {
#     'EndpointConfigName.$': '$.endpoint_config_name',
#     'ProductionVariants': [
#         {
#             'ModelName.$': '$.model_input_id',
#             'VariantName.$': '$.model_variant_input_id'
#         }
#     ]
# }
# # https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateEndpoint.html
# # https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html
# endpoint_input = {
#     'EndpointConfigName.$': '$.endpoint_config_name',
#     'EndpointName.$': '$.endpoint_name'
# }
## choice: if endpoint already exists, updateEndpoint else createEndpoint
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTransformJob.html
testing_transformer_input = {
    'TransformJobName.$': '$.testing_transformer_input_id',
    'ModelName.$': '$.model_input_id',
    'TransformInput': {
        'DataSource': {
            'S3DataSource': {
                'S3DataType': 'S3Prefix',
                'S3Uri.$': '$.test_path'
            }
        },
        'ContentType': 'text/csv'
    },
    'TransformOutput': {
        'S3OutputPath.$': '$.prediction_path'
    },
    'TransformResources': {
        'InstanceCount.$': "$.container_input['InstanceCount']",
        'InstanceType.$': "$.container_input['InstanceType']",
#        'VolumeSizeInGB.$': "$.container_input['VolumeSizeInGB']"
    }
}
prediction_transformer_input = {
    'TransformJobName.$': '$.prediction_transformer_input_id',
    'ModelName.$': '$.model_input_id',
    'TransformInput': {
        'DataSource': {
            'S3DataSource': {
                'S3DataType': 'S3Prefix',
                'S3Uri.$': '$.test_path'
            }
        },
        'ContentType': 'text/csv'
    },
    'TransformOutput': {
        'S3OutputPath.$': '$.prediction_path'
    },
    'TransformResources': {
        'InstanceCount.$': "$.container_input['InstanceCount']",
        'InstanceType.$': "$.container_input['InstanceType']",
#        'VolumeSizeInGB.$': "$.container_input['VolumeSizeInGB']"
    }
}

# input for reporting
# https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html
testing_input = {
    'AppSpecification': {
        'ImageUri.$': '$.processing_image_uri',
        'ContainerArguments.$': '$.testing_input.arguments',
        'ContainerEntrypoint': [ 'python3', '/app/processing.py' ]
    },
    'Environment': {
#        'last_output.$': '$',
        'ExecutionId.$': '$$.Execution.Id',
        'ExecutionName.$': '$$.Execution.Name'
    },
    'ProcessingResources': {
        'ClusterConfig': {
            'InstanceCount.$': "$.processing_input['InstanceCount']",
            'InstanceType.$': "$.processing_input['InstanceType']",
            'VolumeSizeInGB.$': "$.processing_input['VolumeSizeInGB']"
        }
    },
    'ProcessingInputs.$': '$.testing_input.inputs',
    'ProcessingOutputConfig': {
        'Outputs.$': '$.testing_input.outputs'
    },
    'RoleArn.$': f'$.role_arn',
    'ProcessingJobName.$': f'$.testing_input_id'
}
reporting_input = {
    'AppSpecification': {
        'ImageUri.$': '$.processing_image_uri',
        'ContainerArguments.$': '$.reporting_input.arguments',
        'ContainerEntrypoint': [ 'python3', '/app/processing.py' ]
    },
    'Environment': {
#        'last_output.$': '$',
        'ExecutionId.$': '$$.Execution.Id',
        'ExecutionName.$': '$$.Execution.Name'
    },
    'ProcessingResources': {
        'ClusterConfig': {
            'InstanceCount.$': "$.processing_input['InstanceCount']",
            'InstanceType.$': "$.processing_input['InstanceType']",
            'VolumeSizeInGB.$': "$.processing_input['VolumeSizeInGB']"
        }
    },
    'ProcessingInputs.$': '$.reporting_input.inputs',
    'ProcessingOutputConfig': {
        'Outputs.$': '$.reporting_input.outputs'
    },
    'RoleArn.$': f'$.role_arn',
    'ProcessingJobName.$': f'$.reporting_input_id'
}
