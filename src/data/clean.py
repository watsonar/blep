import pandas as pd
import numpy as np
import re

# Functions for data cleaning.

def float_only(val):
    '''
    Takes a string containing a numerical value and returns the first 
    numerical value as a float. If no numerical value, returns string.
    '''
    val = re.sub(',', '', str(val))
    vals = re.findall('\d*\.\d+|\d+', val)
    if len(vals) > 0:
        val = float(vals[0])
    return val

def dict_col_to_cols(df, col, ga=True):
    '''
    Takes a pandas dataframe and specified column where the column
    values are python dictionaries. Uses the key, value pairs of 
    each dictionary to populate values of new or existing columns.
    
    Requires float_only function.

    Args:
        df (pandas dataframe): The pandas dataframe.
        col (str): The name of the column.
        ga (bool): Do the dicts describe guarenteed analysis data?

    Returns:
        df (pandas dataframe): The modified pandas dataframe.
    '''
    for index, row in enumerate(df[col].to_numpy()):
        if pd.notna(row):
            d = eval(row).items()
            d = {key.lower(): value.lower() for key, value in d}
            for key, value in d.items():
                if ga:
                    key = key.replace('crude', '')
                    key = key.replace('fibre', 'fiber')
                    key = key.replace('(min)', 'min')
                    key = key.replace('(max)', 'max')
                    key = re.sub('\s\s+', ' ', key.strip())
                    suffix = re.findall('min|max', value)
                    if len(suffix) == 1:
                        key = ' '.join((key, suffix[0]))
                    units = re.sub('min|max|%', '', value)
                    # if no units:
                    if not re.search('[a-z]', units):
                        key = ' '.join(('%', key))
                    # if units are mg/kg:
                    elif re.search('mg\D*kg', units):
                        key = ' '.join(('%', key))
                        value = float_only(value)/1000000
                if key not in df:
                     df[key] = ''
                df.at[index, key] = float_only(value)
    # Get rid of old column:
    # df.drop(col, axis = 1, inplace = True)
    # Replace any empty values in df with np.nan:
    df.replace('^\s*$', np.nan, regex = True, inplace = True)
    return df

def get_unit_val_col(df, column_name, col_split_regex,
                     unit_name, unit_regex,
                     clear_inconsistent_rows=True,
                     get_denom_col=False,
                     denom_name=None,
                     denom_regex=None):
    '''
    Takes a pandas dataframe and specified column where the column 
    contains a numerical value of a specific unit. Creates a new column 
    to store this value.
    
    Args: 
        df (pandas dataframe): The pandas dataframe.
        col (str): The name of the column.
        col_split_regex (str): How to split the column entries before 
            looking for the value.
        
        unit_name (str): The name of the column to be created.
        unit_regex (str): The regular expression to select the value.
        
        clear_inconsistent_rows (bool): Do you want to discard values 
            from rows where multiple different values were found with 
            the desired unit?
        
        get_denom_col (bool): Do you want ot also create a new column 
            with the value of the unit denominator?
        denom_name (str): If get_denom_col, the name of the denominator
            column to be created.
        denom_regex (str): If get_denom_col, the regular expression to 
            select the value of the denominator.

    Returns:
        df (pandas dataframe): The modified pandas dataframe.
    '''
    df_split = (
            df[column_name].astype(str)
            .str.replace('or',',')
            .str.replace('per', '/')
            .str.split(col_split_regex, expand = True)
            .astype(str) # I don't know why this is necessary but it is
        )
    df_unit = (
            df_split
            .applymap(lambda x: x if re.search(unit_regex, x) else None)
        )
    
    for i in range(df_unit.shape[1]):
        df_unit[0] = df_unit[0].fillna(df_unit[i])
    
    df_unit.rename(columns={0: unit_name}, inplace = True)
    if clear_inconsistent_rows:
        rows_to_clear = df_unit.nunique(axis=1) > 1
        df_unit.loc[rows_to_clear, unit_name] = None
    
    df_unit[unit_name] = (
            df_unit[unit_name]
            .str.extract('(\d*\.\d+|\d+|%)', expand = False)
        )

    df = pd.merge(df, pd.to_numeric(df_unit[unit_name]), 
                  left_index = True, right_index = True)

    if get_denom_col:
        df_unit[denom_name] = (
                df_unit[unit_name]
                .str.extract(denom_regex, expand = False)
            )
        df = pd.merge(df, pd.to_numeric(df_unit[denom_name]), 
                      left_index = True, right_index = True)

    return df
