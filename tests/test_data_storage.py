import unittest
import os
import json
import pandas as pd
import tests.config as config
from aws_mlops.data_storage import DataStorage

class s3fs_for_testing():
    tmp = None
    def __init__(self, *args, **kwargs):
        self.tmp = os.path.dirname(os.path.realpath(__file__))

    def open(self, s3_url, mode='rb'):
        filename = os.path.basename(s3_url)
        path = os.path.join(self.tmp, filename)
        return open(path, mode)

class TestService(unittest.TestCase, DataStorage):
    ds = None
    tmp = None

    def __init__(self, *args, **kwargs):
        self.ds = DataStorage()
        self.ds.s3 = s3fs_for_testing()
        self.tmp = os.path.dirname(os.path.realpath(__file__))
        unittest.TestCase.__init__(self, *args, **kwargs)
        
    def test_checkpoint_and_restore(self):
        data = {'col_1': [0, 1, 2, 3], 'col_2': ['a', 'b', 'c', 'd']}
        df_prepared = pd.DataFrame.from_dict(data)
        df_prepared.index.rename('index', inplace=True)

        self.ds.checkpoint(df_prepared)
        df_restored = self.ds.restore()
        df_restored.set_index('index', inplace=True)

        df_diff = pd.concat([df_prepared, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

    def test_local_save_and_read(self):
        data = {'col_1': [0, 1, 2, 3], 'col_2': ['a', 'b', 'c', 'd']}
        df_prepared = pd.DataFrame.from_dict(data)
        df_prepared.index.rename('index', inplace=True)

        self.ds.local_save(df_prepared, self.tmp)
        df_restored = self.ds.local_read(self.tmp)
        df_restored.set_index('index', inplace=True)

        df_diff = pd.concat([df_prepared, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

    def test_create_dataframe_from_dict(self):
        fh = open(self.tmp + '/config.json')
        json_config = json.load(fh)
        fh.close()

        df_created = self.ds.create_dataframe_from_dict(json_config)
        self.assertTrue('environment' in df_created)
        self.assertTrue('estimator_input.container.version' in df_created)
        self.assertTrue('tuner_input.environment' in df_created)

        df_created = self.ds.create_dataframe_from_dict(json_config, ['container', 'tuner_input'])
        self.assertTrue('environment' in df_created)
        self.assertTrue('estimator_input.container.version' in df_created)
        self.assertFalse('tuner_input.environment' in df_created)

        df_created = self.ds.create_dataframe_from_dict(json_config, ['environment', 'tuner_input'])
        self.assertFalse('environment' in df_created)
        self.assertTrue('estimator_input.container.version' in df_created)
        self.assertFalse('tuner_input.environment' in df_created)

    def test_create_dataframe_from_py(self):
        df_created = self.ds.create_dataframe_from_py(config)
        self.ds.local_save(df_created, self.tmp, 'config.csv', True)
        df_restored = self.ds.local_read(self.tmp, 'config.csv')
        df_diff = pd.concat([df_created, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

        df_created = self.ds.create_dataframe_from_py(config, ['container', 'ContinuousParameter', 'IntegerParameter', 'os', 'git', 'datetime', 'get_commit', 'create_ts', 'create_ts', 'slash_to_dash', 'tuner_input'])
        df_restored = self.ds.local_read(self.tmp, 'config.csv')
        df_diff = pd.concat([df_created, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

        df_created = self.ds.create_dataframe_from_py(config, ['environment', 'ContinuousParameter', 'IntegerParameter', 'os', 'git', 'datetime', 'get_commit', 'create_ts', 'create_ts', 'slash_to_dash', 'tuner_input'])
        self.ds.local_save(df_created, self.tmp, 'config_without_environment.csv', True)
        df_restored = self.ds.local_read(self.tmp, 'config_without_environment.csv')
        df_diff = pd.concat([df_created, df_restored]).drop_duplicates(keep=False)
        self.assertTrue(df_diff.empty)

    def test_save_and_restore_test(self):
        data = {'target': [0, 1, 2, 3], 'identifier': ['a', 'b', 'c', 'd'], 'col_3': ['f', 's', 't', 'f']}
        df_prepared = pd.DataFrame.from_dict(data)

        df_test = self.ds.save_test(df_prepared)
        self.ds.local_save(df_test, self.tmp, 'test.csv', header=False)
        [columns_names, target, identifier] = self.ds.restore_test()
        self.assertEqual(columns_names['list_columns'][0], 'col_3')
        # df_test_restored = self.ds.local_read(self.tmp, 'test.csv')
        df_test_restored = pd.read_csv(os.path.join(self.tmp, 'test.csv'), names=list(columns_names['list_columns']))
        # columns = ['target', 'identifier'] + list(columns_names['list_columns'])
        df_merged = pd.concat([target, identifier, df_test_restored], axis=1)
        # df_merge.columns = columns
        self.assertEqual(df_merged['target'][0], 0)
        self.assertEqual(df_merged['identifier'][0], 'a')
        self.assertEqual(df_merged['col_3'][0], 'f')

        # print('prepared')
        # print(df_prepared)
        # df_diff = pd.concat([df_prepared, df_merged]).drop_duplicates(keep=False)
        # print('df_diff')
        # print(df_diff)
        # print('concat')
        # print(pd.concat([df_prepared, df_merged]))
        # self.assertTrue(df_diff.empty)
 
if __name__ == '__main__':
    unittest.main()