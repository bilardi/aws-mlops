import pandas as pd
from aws_mlops.data_storage import DataStorage
from sklearn.model_selection import train_test_split

class PrepWithPandas():
    def run(self, config_name, config):
        # get dataframe
        input = getattr(config, config_name)['inputs'][0]
        ds = DataStorage(config.source_bucket, config.testing_data_key)
        df = ds.local_read(path=input['S3Input']['LocalPath'], filename=input['InputName'], low_memory=False)
        output_dataframes = []

        # prep df: remember that target column has to be the first column
        # --> add your code - start
        df.insert(1, config.identifier, range(883, 883 + len(df)))
        # --> add your code - end

        if config_name == 'pretraining_input':
            # --> add your code before first split - start
            target = df[config.target]
            no_target = df.drop([config.target], axis = 1)
            target = target.to_frame()
            df = pd.concat([target, no_target], axis = 1)
            # --> add your code before first split - end

            # split df in train and test
            train, test, _, _ = train_test_split(df, df[config.target], test_size=config.test_size, random_state=0)

            # save columns names of test, target and identifier columns
            test = ds.save_test(test, [config.target, config.identifier])

            # --> add your code before second split - start
            train.drop(config.identifier, axis = 1, inplace = True)
            # --> add your code before second split - end

            # split train in final_train and validation
            final_train, validation, _, _ = train_test_split(train, train[config.target], test_size=config.validation_size, random_state=0)
            output_dataframes.append(final_train)
            output_dataframes.append(validation)
            output_dataframes.append(test)
        else: # for preinference there is not modeling but only prediction
            # --> add your code before saving - start
            if config.target in df.columns:
                df.drop(config.target, axis = 1, inplace = True)
            # --> add your code before saving - end

            # save columns names of data and identifier columns
            data = ds.save_test(df, [config.identifier])

            output_dataframes.append(data)

        # saving dataframes: all dataframe without header
        for output in getattr(config, config_name)['outputs']:
            dataframe = output_dataframes.pop(0)
            ds.local_save(dataframe, output['S3Output']['LocalPath'], output['OutputName'], header = False, index = False)

        return 'Dataframes saved'