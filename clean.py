import pandas as pd
import numpy as np
import re

# Functions for data cleaning.

def float_only(val):
    '''
    Takes a string containing a numerical value and returns the first 
    numerical value as a float.
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



##################################



def calc_carbohydrate(df):
    df['% carbohydrate'] = (100 
                            - df['% protein min']
                            - df['% fat min']
                            - df['% fiber max']
                            - df['% moisture max'])
    return df

def calc_dry_matter(df):
    df['% dry matter min'] = (100 - df['% moisture max'])
    df['% carbohydrate dry'] = (df['% carbohydrate'] 
                                / df['% dry matter min'] * 100)
    df['% protein min dry']  = (df['% protein min'] 
                                / df['% dry matter min'] * 100)
    df['% fat min dry']  = (df['% fat min'] 
                            / df['% dry matter min'] * 100)
    df['% fiber max dry']  = (df['% fiber max'] 
                              / df['% dry matter min'] * 100)
    return df

def calc_percent_kcals(df):
    df['calories carbohydrate / 100g'] = df['% carbohydrate'] * 3.5
    df['calories min protein / 100g'] = df['% protein min'] * 3.5
    df['calories min fat / 100g'] = df['% fat min'] * 8.5

    cal_per_100g = (df['calories carbohydrate / 100g']
                    + df['calories min protein / 100g']
                    + df['calories min fat / 100g'])
    
    df['% calories carbohydrate'] = (df['calories carbohydrate / 100g'] 
                                     / cal_per_100g * 100)
    df['% calories min protein'] = (df['calories min protein / 100g'] 
                                    / cal_per_100g * 100)
    df['% calories min fat'] = (df['calories min fat / 100g'] 
                                / cal_per_100g * 100)
    return df

def calc_grams_per_kcal(df):
    df['kcal/kg'] = (df['kcal/kg'].fillna(df['kcal/unit'] 
                     / df['item_vol_oz'] * 35.27396195))
    df['g/kcal'] = 1000 / df['kcal/kg']
    return df

def calc_total_grams(df):
    df['total_mass_lb'] = df['total_mass_lb'].fillna(df['attr_mass_lb'])
    if df['total_mass_lb'].isna().any():
        df['total_mass_lb'] = (df['total_mass_lb']
                               .fillna(df['item_count'] 
                               * df['item_vol_oz'] / 16))
    df['total_mass_g'] = df['total_mass_lb'] * 453.59237
    return df

def calc_total_kcals(df):
    df['total_kcals'] = df['kcal/kg'] * df['total_mass_g'] / 1000
    return df

def calc_usd_per_kcal(df):
    df['usd/kcal'] = df['our_price'] / df['total_kcals']
    return df

def calc_usd_per_gram(df):
    df['usd/g'] = df['our_price'] / df['total_mass_g']
    return df


# PROCESS DATA 

df = pd.read_csv("Chewy/spiders/raw_chewy_data_28_09_2020.csv")

df = dict_col_to_cols(df=df, col='ga_dict', ga=True)
df = dict_col_to_cols(df=df, col='attr_dict', ga=False)

# It is mandatory to report crude protein min, crude fat min, and crude fiber max.
# If protein min or fat min isn't reported, but another protein or fat value is,
# in every case I have checked it is a typo. So:.
df['% protein min'] = df['% protein min'].fillna(df['% protein']).fillna(df['% protein max'])
df['% fat min'] = df['% fat min'].fillna(df['% fat']).fillna(df['% fat max'])
df['% fiber max'] = df['% fiber max'].fillna(df['% fiber']).fillna(df['% fiber min'])
df['% moisture max'] = df['% moisture max'].fillna(df['% moisture']).fillna(df['% moisture min'])

df = df.dropna(thresh = df.shape[0] * 0.5, how = 'all', axis = 1)

df = get_unit_val_col(df, column_name = 'calories', 
                  col_split_regex = '(?<!/) (?=\d)|,|;|:', 
                  unit_name = 'kcal_per_kg', 
                  unit_regex = 'kcal.*kg')

df = get_unit_val_col(df, column_name = 'calories', 
                  col_split_regex = '(?<!/) (?=\d)|,|;|:', 
                  unit_name = 'kcal_per_oz', 
                  unit_regex = 'kcal.*oz|kcal.*ounce')

df = get_unit_val_col(df, column_name = 'calories', 
                  col_split_regex = '(?<!/) (?=\d)|,|;|:', 
                  unit_name = 'kcal_per_cup', 
                  unit_regex = 'kcal.*cup')


df = get_unit_val_col(df, column_name = 'calories', 
                  col_split_regex = '(?<!/) (?=\d)|,|;|:', 
                  unit_name = 'kcal_per_item_volume', 
                  unit_regex = 'kcal.*can|kcal.*pouch|kcl.*pouch|kcal.*unit|kcal.*bowl|kcal.*tray|kcal.*container|kcal.*serving|kcal.*tub|kcal.*pack',
                  clear_inconsistent_rows = False,
                  get_denom_col = True,
                  denom_name = 'item_volume_for_kcal',
                  denom_regex = '((?<=\/).*?\d+\.?\d+)')

df = get_unit_val_col(df, column_name = 'name', 
                  col_split_regex = ',', 
                  unit_name = 'item_count', 
                  unit_regex = 'case of')

df['item_count'] = df['item_count'].fillna(1)

df = get_unit_val_col(df, column_name = 'name', 
                  col_split_regex = ',', 
                  unit_name = 'item_oz', 
                  unit_regex = 'oz|ounce')

df = get_unit_val_col(df, column_name = 'name', 
                  col_split_regex = ',', 
                  unit_name = 'total_mass_lb', 
                  unit_regex = 'lb|pound|Pound')

df.rename(columns={'weight': 'attr_mass_lb'}, inplace = True)
# df['total_mass_lb'] = df['total_mass_lb'].fillna(df['attr_mass_lb'])

"""
df = calc_carbohydrate(df)
df = calc_dry_matter(df)
df = calc_percent_kcals(df)
df = calc_grams_per_kcal(df)
df = calc_total_grams(df)
df = calc_usd_per_gram(df)
df = calc_total_kcals(df)
df = calc_usd_per_kcal(df)
"""

df.to_csv('test.tsv', sep='\t')
