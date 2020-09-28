import pandas as pd
import numpy as np
import re

df = pd.read_csv("Chewy/spiders/raw_chewy_spider.csv")

def float_only(val):
    val = re.sub(',', '', str(val))
    vals = re.findall('\d*\.\d+|\d+', val)
    if len(vals) > 0:
        val = float(vals[0])
    return val

def dict_col_to_cols(df, col, ga=True):
    for index, row in enumerate(df[col].to_numpy()):
        if pd.notna(row):
            d = {key.lower(): value.lower() for key, value in eval(row).items()}
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
                    key = key.replace('crude', '')
                    key = key.replace('fibre', 'fiber')
                    key = re.sub('\s\s+', ' ', key.strip())
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
                     denom_regex=None,
                     remove_unit=True):
    ''' Looks for a number with a specific unit in a column, and makes a
    column for that unit. 
    '''
    df_unit_only = df[column_name].astype(str).str.replace('or',',').str.split(col_split_regex, expand = True)
    df_unit_as_str = df_unit_only.astype(str)
    df_unit = df_unit_as_str.applymap(lambda x: x if re.search(unit_regex, x) else None)
    
    for i in range(df_unit.shape[1]):
        df_unit[0] = df_unit[0].fillna(df_unit[i])
    
    df_unit.rename(columns={0: unit_name}, inplace = True)
    if clear_inconsistent_rows:
        rows_to_clear = df_unit.nunique(axis=1) > 1
        df_unit.loc[rows_to_clear, unit_name] = None
    
    df_unit[unit_name] = df_unit[unit_name].str.extract('(\d*\.\d+|\d+|%)', expand = False)

    df = pd.merge(df, pd.to_numeric(df_unit[unit_name]), left_index = True, right_index = True)

    if get_denom_col:
        df_unit[denom_name] = df_unit[unit_name].str.extract(denom_regex, expand = False)
        df = pd.merge(df, pd.to_numeric(df_unit[denom_name]), left_index = True, right_index = True)

    return df

def calc_carbohydrate(df):
    df['% carbohydrate'] = 100 - df['% protein min'] \
                               - df['% fat min'] \
                               - df['% fiber max'] \
                               - df['% moisture max']
    return df

def calc_dry_matter(df):
    df['% dry matter min'] = 100 - df['% moisture max']
    df['% carbohydrate dry'] = df['% carbohydrate'] / df['% dry matter min'] * 100
    df['% protein min dry']  = df['% protein min'] / df['% dry matter min'] * 100
    df['% fat min dry']  = df['% fat min'] / df['% dry matter min'] * 100
    df['% fiber max dry']  = df['% fiber max'] / df['% dry matter min'] * 100
    return df

def calc_percent_kcals(df):
    df['calories carbohydrate / 100g'] = df['% carbohydrate'] * 3.5
    df['calories min protein / 100g'] = df['% protein min'] * 3.5
    df['calories min fat / 100g'] = df['% fat min'] * 8.5
    cal_per_100g = df['calories carbohydrate / 100g'] \
                 + df['calories min protein / 100g'] \
                 + df['calories min fat / 100g']
    df['% calories carbohydrate'] = df['calories carbohydrate / 100g'] / cal_per_100g * 100
    df['% calories min protein'] = df['calories min protein / 100g'] / cal_per_100g * 100
    df['% calories min fat'] = df['calories min fat / 100g'] / cal_per_100g * 100
    return df

def mass_per_kcal(df):
    df['kcal/kg'] = df['kcal/kg'].fillna(df['kcal/can'] / df['item_vol_oz'] * 35.27396195)
    df['g/kcal'] = 1000 / df['kcal/kg']
    return df

df = dict_col_to_cols(df=df, col='ga_dict', ga=True)
df = dict_col_to_cols(df=df, col='attr_dict', ga=False)

# It is mandatory to report crude protein min, crude fat min, and crude fiber max.
# If protein min or fat min isn't reported, but another protein or fat value is,
# in every case I have checked it is a typo. So:.
df['% protein min'] = df['% protein min'].fillna(df['% protein']).fillna(df['% protein max'])
df['% fat min'] = df['% fat min'].fillna(df['% fat']).fillna(df['% fat max'])
df['% fiber max'] = df['% fiber max'].fillna(df['% fiber']).fillna(df['% fiber min'])
df['% moisture max'] = df['% moisture max'].fillna(df['% moisture']).fillna(df['% moisture min'])

# df = df.dropna(thresh = df.shape[0] * 0.5, how = 'all', axis = 1)

df = get_unit_val_col(df, column_name = 'calories', 
                  col_split_regex = '(?<!/) (?=\d)|,|;|:', 
                  unit_name = 'kcal/kg', 
                  unit_regex = 'kcal.*kg')

df = get_unit_val_col(df, column_name = 'calories', 
                  col_split_regex = '(?<!/) (?=\d)|,|;|:', 
                  unit_name = 'kcal/can', 
                  unit_regex = 'kcal.*can',
                  clear_inconsistent_rows = False,
                  get_denom_col = True,
                  denom_name = 'can_volume_for_cals',
                  denom_regex = '((?<=\/).*?\d+\.?\d+)')

df = get_unit_val_col(df, column_name = 'name', 
                  col_split_regex = ',', 
                  unit_name = 'item_count', 
                  unit_regex = 'case')

df = get_unit_val_col(df, column_name = 'name', 
                  col_split_regex = ',', 
                  unit_name = 'item_vol_oz', 
                  unit_regex = 'oz',
                  clear_inconsistent_rows = False)

df = get_unit_val_col(df, column_name = 'weight',
                  col_split_regex = '(?!)i',
                  unit_name = 'weight_lbs',
                  unit_regex = 'pounds',
                  clear_inconsistent_rows = False)
                  # this col_split_regex matches to nothing.

print('calc_carb')
df = calc_carbohydrate(df)
print(df)
print('calc_dry_matter')
df = calc_dry_matter(df)
print(df)
print('calc_percent_kcals')
df = calc_percent_kcals(df)
print(df)
print('mass_per_kcal')
df = mass_per_kcal(df)

df.to_csv('test.tsv', sep='\t')
