Usage
=====

The `AWS Step Functions <https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html>`_ manages your ML cycle of data processing, modeling and testing or prediction with your best model.
You can find all python scripts that you have to prepare for your MLOps solution in the folder **example**:

* **config.py**, it contains all you want to configure for using the aws_mlops library
* **definitions.py**, it contains all you want to configure for creating your step functions
* **processing.py**, probably you can copy it and it is not necessary to modify it
* **Dockerfile**, it contains what you need for running the script named processing.py
* **prep_with_pandas.py**, it contains your code for data processing and it is loaded by processing.py
* **test_with_pandas.py**, it contains your code for testing and it is the script loaded by processing.py

You can also find the *ipynb* files that they are useful to prepare your python scripts:

* **prep_with_pandas.ipynb** for **prep_with_pandas.py**
* **test_with_pandas.ipynb** for **test_with_pandas.py**

And there are some bash scripts for creating your CI / CD system:

* **test.sh** for testing python library and step functions deployment
* **test_docker.sh** for testing the scripts you can call from processing.py
* **build_image.sh** for building your image and saving it on AWS ECR
* **deploy.sh** for deploying step functions and lambda of your infrastructure

Example
#######

You need an infrastructure with a process for

* preparing the raw data for your training by AWS Sagemaker Autopilot
* running Autopilot
* inference with your best model and your test data
* testing and saving the prediction data, metrics and attributes used

When you know the initial hyperparameters that you can use, you can setup the config.py and

* preparing the raw data for your training
* training and tuning your model
* inference with your best model and your test data
* testing and saving the prediction data, metrics and attributes used

And the last two points have to be usable for

* inference with your best model and your new data
* saving the prediction data, metrics and attributes used

When you have prepared the python scripts listed above, you have to

* commit your changes and push on your repo
* proceed with the commands for deploying described in the `Development <https://aws-mlops.readthedocs.io/latest/development.html>`_ Section and paragraph **Deploy on AWS**

When you have deployed the infrastructure, you can use the **example/mlops.ipynb** for calling the whole cycle or only a specific piece.

The secret is to version all: data, code and model that you use for defining that prediction.
It is important to version any change for the analysis step.

If you need to improve your configuration or your scripts, the best way is

* commit any change of your python scripts listed above, thus the s3 key will be different for commit
* if you change only the raw/new data, the s3 key would be different for datatime, but you also can fix it for your testing
* if you have to test your change, deploy an infrastructure for your branch, thus the s3 key will be different from production
