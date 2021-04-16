import pandas as pd
import numpy as np

# Functions for calculating macros, prices, etc.

def calc_carbohydrate(df):
    df['%_carbohydrate'] = (100 
                            - df['%_protein_min']
                            - df['%_fat_min']
                            - df['%_fiber_max']
                            - df['%_misc_components']
                            - df['%_moisture_max'])
    df['%_carbohydrate'] = df['%_carbohydrate'].mask(df['%_carbohydrate'] < 0, 0)
    return df

def calc_dry_matter(df):
    df['%_dry_matter_min'] = (100 - df['%_moisture_max'])
    df['%_carbohydrate_dry'] = (df['%_carbohydrate'] 
                                / df['%_dry_matter_min'] * 100)
    df['%_protein_min_dry']  = (df['%_protein_min'] 
                                / df['%_dry_matter_min'] * 100)
    df['%_fat_min_dry']  = (df['%_fat_min'] 
                            / df['%_dry_matter_min'] * 100)
    return df

def calc_percent_kcals(df):
    df['calories_carbohydrate_per_100g'] = df['%_carbohydrate'] * 3.5
    df['calories_min_protein_per_100g'] = df['%_protein_min'] * 3.5
    df['calories_min_fat_per_100g'] = df['%_fat_min'] * 8.5

    cal_per_100g = (df['calories_carbohydrate_per_100g']
                    + df['calories_min_protein_per_100g']
                    + df['calories_min_fat_per_100g'])
    
    df['%_calories_carbohydrate'] = (df['calories_carbohydrate_per_100g'] 
                                     / cal_per_100g * 100)
    df['%_calories_min_protein'] = (df['calories_min_protein_per_100g'] 
                                    / cal_per_100g * 100)
    df['%_calories_min_fat'] = (df['calories_min_fat_per_100g'] 
                                / cal_per_100g * 100)
    return df

def calc_kcal_per_product(df):
    df['kcal_per_product'] = np.nan
  
    df_item_vals = df[df['kcal_per_item'].notnull() & df['item_count'].notnull()].copy()
    df_item_vals['kcal_per_product'] = df_item_vals['kcal_per_product'].fillna(df_item_vals['kcal_per_item'] * df_item_vals['item_count'])
    df.update(df_item_vals)
    
    df_mass_vals = df[df['kcal_per_lb'].notnull() & df['total_mass_lb'].notnull()].copy()
    df_mass_vals['kcal_per_product'] = df_mass_vals['kcal_per_product'].fillna(df_mass_vals['kcal_per_lb'] * df_mass_vals['total_mass_lb'])
    df.update(df_mass_vals)
    
    df_volume_vals = df[df['kcal_per_oz'].notnull() & df['item_oz'].notnull() & df['item_count'].notnull()].copy()
    df_volume_vals['kcal_per_product'] = df_volume_vals['kcal_per_product'].fillna(df_volume_vals['kcal_per_oz'] * df_volume_vals['item_oz'] * df_volume_vals['item_count'])
    df.update(df_volume_vals)
    
    return df
<<<<<<< HEAD

"""
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
"""
=======
>>>>>>> master
