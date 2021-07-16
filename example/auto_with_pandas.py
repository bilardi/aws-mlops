from aws_mlops.data_storage import DataStorage
from sklearn.model_selection import train_test_split

class AutoWithPandas():
    def run(self, config_name, config):
        # get dataframe
        input = getattr(config, config_name)['inputs'][0]
        ds = DataStorage(config.source_bucket, config.testing_data_key)
        df = ds.local_read(path=input['S3Input']['LocalPath'], filename=input['InputName'], low_memory=False)

        # prep df: it is indifferent the target column position
        df.insert(1, config.identifier, range(883, 883 + len(df)))
        train, test, _, _ = train_test_split(df, df[config.target], test_size=config.test_size, random_state=0)
        train.drop('id', axis = 1, inplace = True)
        test = ds.save_test(test, [config.target, config.identifier])

        # saving dataframes
        output = getattr(config, config_name)['outputs'][0]
        # train with header
        ds.local_save(train, output['S3Output']['LocalPath'], output['OutputName'], header = True, index = False)
        output = getattr(config, config_name)['outputs'][1]
        # test without header
        ds.local_save(test, output['S3Output']['LocalPath'], output['OutputName'], header = False, index = False)

        return 'Dataframes saved'