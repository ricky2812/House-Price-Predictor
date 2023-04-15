import pandas as pd
import numpy as np
import matplotlib
matplotlib.rcParams['figure.figsize'] = (20, 10)
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.model_selection import ShuffleSplit, cross_val_score, GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeRegressor
import pickle
import json

def make_model(filename):
    df1 = pd.read_csv("data/"+filename+".csv")

    df2 = df1.drop(['Resale', 'MaintenanceStaff', 'Gymnasium', 'SwimmingPool', 'LandscapedGardens',
       'JoggingTrack', 'RainWaterHarvesting', 'IndoorGames', 'ShoppingMall',
       'Intercom', 'SportsFacility', 'ATM', 'ClubHouse', 'School',
       '24X7Security', 'PowerBackup', 'CarParking', 'StaffQuarter',
       'Cafeteria', 'MultipurposeRoom', 'Hospital', 'WashingMachine',
       'Gasconnection', 'AC', 'Wifi', "Children'splayarea", 'LiftAvailable',
       'BED', 'VaastuCompliant', 'Microwave', 'GolfCourse', 'TV',
       'DiningTable', 'Sofa', 'Wardrobe', 'Refrigerator'], axis='columns')
    df2['bhk'] = df2['No. of Bedrooms']
    df2.drop(['No. of Bedrooms'], axis='columns', inplace=True)

    df3 = df2.copy()
    df3['Price_per_sqft'] = df3['Price'] / df3['Area']
    df3.Location = df3.Location.apply(lambda x: x.strip())

    location_stats = df3.groupby('Location')['Location'].agg('count').sort_values(ascending=False)
    location_stats_less_than_10 = location_stats[location_stats <= 10]
    df3.Location = df3.Location.apply(lambda x: 'other' if x in location_stats_less_than_10 else x)

    df4 = df3[~(df3.Area / df3.bhk < 300)]

    def remove_pps_outliers(df):
        df_out = pd.DataFrame()
        for key, subdf in df.groupby('Location'):
            m = np.mean(subdf.Price_per_sqft)
            st = np.std(subdf.Price_per_sqft)
            reduced_df = subdf[(subdf.Price_per_sqft > (m-st)) & (subdf.Price_per_sqft <= (m+st))]
            df_out = pd.concat([df_out, reduced_df], ignore_index=True)
        return df_out
    df5 = remove_pps_outliers(df4)

    def remove_bhk_outliers(df):
        exclude_indices = np.array([])
        for location, location_df in df.groupby('Location'):
            bhk_stats = {}
            for bhk, bhk_df in location_df.groupby('bhk'):
                bhk_stats[bhk] = {
                    'mean': np.mean(bhk_df.Price_per_sqft),
                    'std': np.std(bhk_df.Price_per_sqft),
                    'count': bhk_df.shape[0]
                }
            for bhk, bhk_df in location_df.groupby('bhk'):
                stats = bhk_stats.get(bhk-1)
                if stats and stats['count'] > 5:
                    exclude_indices = np.append(exclude_indices, bhk_df[bhk_df.Price_per_sqft < (stats['mean'])].index.values)
        return df.drop(exclude_indices, axis='index')
    
    df6 = remove_bhk_outliers(df5)
    df7 = df6.drop(['Price_per_sqft'], axis='columns')
    dummies = pd.get_dummies(df7.Location)
    df8 = pd.concat([df7, dummies.drop('other', axis='columns')], axis='columns')
    df9 = df8.drop(['Location'], axis='columns')



    X = df9.drop(['Price'], axis='columns')
    Y = df9.Price
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=10)

    lr_clf = LinearRegression()
    lr_clf.fit(X_train, Y_train)
    lr_clf.score(X_test, Y_test)

    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    cross_val_score(LinearRegression(), X, Y, cv=cv)

    
    def find_best_model_using_gridsearchcv(X, Y):
        algos={
            'linear_regression': {
                'model': LinearRegression(),
                'params': {
                    'normalize': [True, False]
                }
            },
            'lasso': {
                'model': Lasso(),
                'params': {
                    'alpha': [1, 2],
                    'selection': ['random', 'cyclic']
                }
            },
            'decision_tree': {
                'model': DecisionTreeRegressor(),
                'params': {
                    'criterion': ['mse', 'friedman_mse'],
                    'splitter': ['best', 'random']
                }
            }
        }
        scores = []
        cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
        for algo_name, config in algos.items():
            gs = GridSearchCV(config['model'], config['params'], cv=cv, return_train_score=False)
            gs.fit(X, Y)
            scores.append({
                'model': algo_name,
                'best_score': gs.best_score_,
                'best_params': gs.best_params_
            })

        return pd.DataFrame(scores, columns=['model', 'best_score', 'best_params'])

    find_best_model_using_gridsearchcv(X, Y)

    def predict_price(location, sqft, bhk):
        loc_index = np.where(X.columns==location)[0][0]
        x = np.zeros(len(X.columns))
        x[0] = sqft
        x[1] = bhk
        if loc_index >= 0:
            x[loc_index] = 1
        return lr_clf.predict([x])[0]

    def export_files():
        with open('model/{}_home_prices_model.pickle'.format(filename), 'wb') as f:
            pickle.dump(lr_clf, f)

        columns = {
            'data_columns': [col.lower() for col in X.columns]
        }
        with open("model/{}_columns.json".format(filename),"w") as f:
            f.write(json.dumps(columns))
    export_files()

def main():
    list_of_city = ['Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai']
    for city in list_of_city:
        print("Processing {}".format(city))
        make_model(city)
        print("Done processing {}".format(city))
    print("All models are ready")
if __name__ == "__main__":
    main()