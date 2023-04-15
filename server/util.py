import json
import pickle
import numpy as np
import warnings
warnings.filterwarnings('ignore')


__locations = None
__data_columns = None
__model = None



def get_estimated_price(city,location, sqft, bhk):
    load_saved_artifacts(city)
    try:
        loc_index = __data_columns.index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bhk
    if loc_index >= 0:
        x[loc_index] = 1
    
    price = int(__model.predict([x])[0])
    format_price = str(price)
    if len(format_price) > 7:
        format_price = 'Rs. ' + format_price[:-7] + 'Crore ' + format_price[-7:-5] + 'Lakhs'
    elif len(format_price) > 5:
        format_price = 'Rs. ' + format_price[:-5] + '.' + format_price[-5:-3] + 'Lakhs '
    else:
        format_price = 'Rs.' + format_price[:-3] + 'K'
    return format_price
    
def get_city_names():
    return ['Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai']

def get_location_names(city):
    load_saved_artifacts(city)
    return __locations

def load_saved_artifacts(city):
    global __data_columns
    global __locations

    with open("artifacts/{}_columns.json".format(city.lower()), 'r') as f:
    # with open("server/artifacts/Bangalore_columns.json", 'r') as f:
        __data_columns = json.load(f)['data_columns']
        __locations = __data_columns[3:]

    global __model
    with open("artifacts/{}_home_prices_model.pickle".format(city.lower()), 'rb') as f:
    # with open("server/artifacts/Bangalore_home_prices_model.pickle", 'rb') as f:
        __model = pickle.load(f)


if __name__ == '__main__':
    print(get_location_names('kolkata'))
    print(get_estimated_price('bangalore','Jakkur', 1000, 3))
    print(get_estimated_price('bangalore','Jakkur', 1000, 2))
    print(get_estimated_price('kolkata','new town', 1600, 4)) # other location
    print(get_estimated_price('kolkata','barasat', 1400, 3)) # other location