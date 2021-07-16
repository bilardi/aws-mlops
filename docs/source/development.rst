Development
===========

The environments for development can be many: you can organize a **CI/CD system** with your favorite software.
The primary features of your CI/CD are: having a **complete environment for**

* **development** for each developer, to implement something and for running unit tests 
* **staging** for running unit and integration tests, to check everything before release
* **production**

If you want to use AWS CDK and AWS CodePipeline, you can see these repositories before to implement your version

* `aws-simple-pipeline <https://github.com/bilardi/aws-simple-pipeline/>`_ for using a library ready
* `aws-tool-comparison <https://github.com/bilardi/aws-tool-comparison/tree/master/cdk/python/>`_ for seeing its implementation

When you add the data management in your CD cycle, you have to add the data versioning:

* the system improved in the folder named example, it provides s3 key with branch, environment, commit and datatime
* so you can have a **complete environment for** each combo of them

This is important to commit any change for the analysis step.

Run tests
#########

.. code-block:: bash

    cd aws-mlops/
    npm install
    pip3 install --upgrade -r example/requirements.txt
    python3 -m unittest discover -v
    # even with functional and infrastructure tests
    export AWS_PROFILE=your-account
    bash example/test.sh

Improve your python scripts for processing by Jupyter
#####################################################

.. code-block:: bash

    cd aws-mlops/
    docker run --rm -p 8888:8888 -e JUPYTER_ENABLE_LAB=yes -e AWS_PROFILE=your-account -v $HOME/.aws/credentials:/home/jovyan/.aws/credentials:ro -v "$PWD":/home/jovyan/ jupyter/datascience-notebook

You can find two ipynb files in the folder named example: they can help you to improve your code for the processing steps.

Test your python scripts
########################

If you did never push an image on your repository, run the commands of **Deploy on AWS** paragraph before run the docker.

.. code-block:: bash

    cd aws-mlops/
    export AWS_PROFILE=your-account
    export STAGE=development
    bash example/test_docker.sh

Deploy on AWS
#############

.. code-block:: bash

    cd aws-mlops/
    export AWS_PROFILE=your-account
    export STAGE=development
    bash example/deploy.sh

Remove on AWS
#############

The stack has the tags necessary for being deleted itself, if you use the `aws-saving <https://github.com/bilardi/aws-saving/>`_.
Or you can run the commands below to remove by Serverless only the environment that you want to delete:

.. code-block:: bash

    cd aws-mlops/
    export AWS_PROFILE=your-account
    SLS_DEBUG=* sls remove --stage development
