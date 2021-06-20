Usage
=====

The `AWS Step Functions manages <https://docs.aws.amazon.com/step-functions/latest/dg/connect-sagemaker.html>`_ your ML cycle of data processing, modelling and testing or inference of the best model.
You can find all python scripts that you have to prepare for your MLOps solution in the folder **example**:

* **config.py**, it contains all you want to configure for using the aws_mlops library and creating your step functions
* **processing.py**, probably you can copy it and it is not necessary to modify it
* **prep_with_pandas.py**, it contains your code for data processing and it is loaded by processing.py
* **test_with_pandas.py**, it contains your code for testing and it is the script loaded by processing.py

You can also find the *ipynb* files that they are useful to prepare your python scripts:

* **prep_with_pandas.ipynb** for **prep_with_pandas.py**
* **test_with_pandas.ipynb** for **test_with_pandas.py**

Example
#######

You need an infrastructure with a process for

* preparing the raw data for your training
* training and tuning
* inference with your best model and your test data
* testing and saving the prediction data, metrics and attributes used

And the last two points have to be usable for

* inference with your best model and your new data
* saving the prediction data, metrics and attributes used

When you have prepared the python scripts listed above, you can

* use the **example/mlops.ipynb** for creating step functions json
* proceed with the commands for deploying described in the `Development <https://aws-mlops.readthedocs.io/latest/development.html>`_ Section and paragraph **Deploy on AWS**

When you have deployed the infrastructure, you can use the **example/mlops.ipynb** for calling the whole cycle or only the process for inference and saving data.

The secret is to version all: data, code and model that you use for defining that prediction.
It is important to version any change for the analysis step.

If you need to improve your configuration or your scripts, the best way is

* commit any change of your python scripts listed above, thus the s3 key will be different for commit
* if you change only the raw data, the s3 key will be different for datatime
* if you have to test your change, deploy an infrastructure for your branch, thus the s3 key will be different from production
