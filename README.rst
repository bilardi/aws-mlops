Getting started
===============

AWS MLOps package is implemented to help you like a framework for deploying what it is necessary to manage your models.

The goal is to implement this package to keep your focus on your prep and test code using the AWS SageMaker services, AWS Step Functions and AWS Lambda.

It is part of the `educational repositories <https://github.com/pandle/materials>`_ to learn how to write stardard code and common uses of the TDD and CI / CD.

Prerequisites
#############

You can use `Serverless framework <https://www.serverless.com/framework/docs/providers/aws/guide/installation/>`_ for deploying the AWS services:
if you want to use the guide below, you have to install `npm <https://www.npmjs.com/get-npm>`_ (`Node Package Manager <https://docs.npmjs.com/cli/v6/commands>`_) before.

If you want to use another AWS tool, you can see the repository `aws-tool-comparison <https://github.com/bilardi/aws-tool-comparison>`_ before to implement your version.

Installation
############

The package is not self-consistent. So you have to download the package by github and to install the requirements before to deploy the **example** on AWS:

.. code-block:: bash

    git clone https://github.com/bilardi/aws-mlops
    cd aws-mlops/
    npm install
    export AWS_PROFILE=your-account
    export STAGE=studio
    bash example/deploy.sh

Or if you want to use this package into your code, you can install by python3-pip:

.. code-block:: bash

    pip3 install aws_mlops
    python3
    >>> import aws_mlops
    >>> help(aws_mlops)

Read the documentation on `readthedocs <https://aws-mlops.readthedocs.io/en/latest/>`_ for

* Usage
* Development

Change Log
##########

See `CHANGELOG.md <https://github.com/bilardi/aws-mlops/blob/master/CHANGELOG.md>`_ for details.

License
#######

This package is released under the MIT license.  See `LICENSE <https://github.com/bilardi/aws-mlops/blob/master/LICENSE>`_ for details.
