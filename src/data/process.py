import pandas as pd

# Functions for calculating macros, prices, etc.

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
