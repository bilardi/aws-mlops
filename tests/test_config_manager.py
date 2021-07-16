import unittest
import json
from botocore.exceptions import ClientError

import aws_mlops.config_manager as cm

class S3Client():
    go = None
    po = None
    do = False
    goe = False
    poe = False
    doe = False
    def __init__(self):
        with open('tests/s3-get-object.json') as json_file:
            go = json.load(json_file)
            go['Body'] = StreamingBody(go['Body'])
            self.go = go
        with open('tests/s3-put-object.json') as json_file:
            self.po = json.load(json_file)
        with open('tests/s3-delete-object.json') as json_file:
            self.do = json.load(json_file)
    def get_object(self, Bucket, Key):
        if isinstance(Bucket, str) and isinstance(Key, str) and not self.goe:
            return self.go
        else:
            raise ClientError({'Error':{'Code':'NoSuchKey'}}, 'NoSuchKey')
    def put_object(self, ACL, Bucket, Key, Body):
        if isinstance(ACL, str) and isinstance(Bucket, str) and isinstance(Key, str) and isinstance(Body, bytes) and not self.poe:
            return self.po
        else:
            return {}
    def delete_object(self, Bucket, Key):
        if isinstance(Bucket, str) and isinstance(Key, str) and not self.doe:
            return self.do
        else:
            return {}        

class StreamingBody():
    body = None
    def __init__(self, body):
        self.body = body
    def read(self):
        return self.body

class SsmClient():
    gp = None
    pp = None
    dp = None
    gpe = False
    def __init__(self):
        with open('tests/ssm-get-parameter.json') as json_file:
            self.gp = json.load(json_file)
        with open('tests/ssm-put-parameter.json') as json_file:
            self.pp = json.load(json_file)
        with open('tests/ssm-delete-parameter.json') as json_file:
            self.dp = json.load(json_file)
    def get_parameter(self, Name = 'test'):
        if isinstance(Name, str) and not self.gpe:
            return self.gp
        else:
            raise ClientError({'Error':{'Code':'ParameterNotFound'}}, 'NotFound')
    def put_parameter(self, Name='test', Value='string', Type='String', Overwrite=True):
        if isinstance(Name, str) and isinstance(Value, str) and isinstance(Type, str) and isinstance(Overwrite, bool):
            return self.pp
    def delete_parameter(self, Name='test'):
        if isinstance(Name, str):
            return self.dp

class SfnClient():
    de = None
    def __init__(self):
        with open('tests/sfn-describe-execution.json') as json_file:
            self.de = json.load(json_file)
    def describe_execution(self, executionArn = 'test'):
        if isinstance(executionArn, str):
            return self.de

class TestManageConfig(unittest.TestCase):
    event = None

    def __init__(self, *args, **kwargs):
        cm.s3 = S3Client()
        cm.ssm = SsmClient()
        cm.sfn = SfnClient()
        with open('tests/config.json') as json_file:
            self.event = json.load(json_file)
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_main(self):
        self.assertTrue('service' in self.event)
        self.assertFalse('ModelName' in self.event)

        cm.s3.goe = True
        result = cm.main(self.event)
        self.assertEqual(result['body']['Parameter'], 'from-event') # get-event
        self.assertTrue('Model', result['body']) # get-execution
        self.assertFalse('VersionId' in result['body']) # get-s3

        cm.s3.goe = False
        result = cm.main(self.event)
        self.assertEqual(result['body']['Parameter'], 'from-event') # get-event
        self.assertTrue('Model', result['body']) # get-execution
        self.assertFalse('VersionId' in result['body']) # get-s3

        del(self.event['last_output']['Parameter'])

        cm.s3.goe = True
        result = cm.main(self.event)
        self.assertEqual(result['body']['Parameter'], 'Initial') # get-execution
        self.assertTrue('Model', result['body']) # get-execution
        self.assertFalse('VersionId' in result['body']) # get-s3

        cm.s3.goe = False
        result = cm.main(self.event)
        self.assertEqual(result['body']['Parameter'], 'from-s3') # get-s3
        self.assertTrue('Model', result['body']) # get-execution
        self.assertFalse('VersionId' in result['body']) # get-s3

if __name__ == '__main__':
    unittest.main()