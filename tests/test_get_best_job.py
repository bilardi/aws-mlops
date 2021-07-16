import unittest
import json

import aws_mlops.get_best_job as bj

class SmClient():
    dtj = None
    def __init__(self):
        with open('tests/sm-describe-trainig-job.json') as json_file:
            self.dtj = json.load(json_file)
    def describe_training_job(self, TrainingJobName = 'test'):
        if isinstance(TrainingJobName, str):
            return self.dtj

class TestGetBestJob(unittest.TestCase):
    si = None
    sm = None

    def __init__(self, *args, **kwargs):
        bj.sm = SmClient()
        with open('tests/sm-step-input.json') as json_file:
            self.si = json.load(json_file)
        unittest.TestCase.__init__(self, *args, **kwargs)
    
    def test_main(self):
        result = bj.main(self.si, None)
        self.assertEqual(result['statusCode'], 200)
        self.assertEqual(result['body']['HyperParameter']['eval_metric'], 'rmse')
        self.assertEqual(result['body']['test_input']['key'], 'value')
        self.assertEqual(result['body']['TrainingJobName'], 'test')

if __name__ == '__main__':
    unittest.main()