import json
import pandas as pd
from aws_mlops.data_storage import DataStorage
from aws_mlops.config_manager import ConfigManager
import sklearn.metrics as metrics

class TestWithPandas():
    def run(self, config_name, config):
        # restore columns nams of test/data, [target] and identifier columns
        ds = DataStorage(config.source_bucket, config.testing_data_key)
        # downloading configuration used by config_manager.run()
        cm = ConfigManager()
        # for sagemaker processing
        config_downloaded = cm.get_config_by_s3(config.source_bucket, f'{config.key}/config.json')
        if config_downloaded == {}:
            # for local & codebuild testing
            config_downloaded = config.dictionary_from_module(config)
        print(config_downloaded)
        identifier = None
        df = None
        output_dataframes = []

        # loading dataframes
        input = getattr(config, config_name)['inputs'][0]
        score = ds.local_read(path=input['S3Input']['LocalPath'], filename=input['InputName'], header=None, low_memory=False)
        score.columns = [config.score] # pay attention to use header = None else the first row will be replaced
        if config_name == 'testing_input' and len(getattr(config, config_name)['inputs']) == 2:
            input = getattr(config, config_name)['inputs'][1]
            [columns_names, target, identifier] = ds.restore_test([config.target, config.identifier])
            test = ds.local_read(path=input['S3Input']['LocalPath'], filename=input['InputName'], header=None, low_memory=False)
            test.columns = list(columns_names['list_columns']) # pay attention to use header = None else the first row will be replaced
            # join datasets
            df = pd.concat([identifier, target, score, test], axis=1)
            # report datasets
            report = pd.DataFrame({
                'Mean squared error': [metrics.mean_squared_error(df[config.target], df[config.score])],
                'Mean absolute error': [metrics.mean_absolute_error(df[config.target], df[config.score])]
            })
            if 'model_input_id' in config_downloaded:
                # if the model is better, then save the model identificator on ssm
                cm.save_config_by_ssm(config.models_ssm, config_downloaded['model_input_id'])
            else:
                print('model_input_id not found')
        else:
            [columns_names, identifier] = ds.restore_test([config.identifier])
            # join datasets
            df = pd.concat([identifier, score], axis=1)
            report = pd.DataFrame({})

        # prediction datasets
        prediction = df[[config.identifier, config.score]]
        output_dataframes.append(prediction)
        output_dataframes.append(report)

        # saving dataframes
        for output in getattr(config, config_name)['outputs']:
            dataframe = output_dataframes.pop(0)
            ds.local_save(dataframe, output['S3Output']['LocalPath'], output['OutputName'], header = True, index = False)

        return 'Dataframes and metrics saved'
