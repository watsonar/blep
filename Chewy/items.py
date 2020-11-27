# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from itemloaders.processors import MapCompose, TakeFirst
import re

def strip_list_or_dict(item_ele):
    if type(item_ele) is list:
        item_ele = [i.strip() for i in item_ele]
    elif type(item_ele) is dict:
        item_ele = {key.strip(): value.strip() for key, value in item_ele.items()}
    return item_ele

# def remove_empty(item_ele):
#     return item_ele if item_ele else None

def remove_commas_from_numbers(item_ele):
    return re.sub(r'(?<=\d),(?=\d)', '', item_ele)

def remove_everything_before_digits(item_ele):
    return re.sub(r'^\D+', '', item_ele)

# def replace_chars(item_ele):
#     translations = str.maketrans({',': ';'})
#     item_ele = item_ele.translate(translations)
#     return item

class ChewyItem(scrapy.Item):
    name = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    url = Field(
        output_processor = TakeFirst()
    )
    our_price = Field(
        input_processor = MapCompose(str.strip, 
                                     remove_everything_before_digits),
        output_processor = TakeFirst()
    )
    list_price = Field(
        input_processor = MapCompose(str.strip, 
                                     remove_everything_before_digits),
        output_processor = TakeFirst()
    )
    calories = Field(
        input_processor = MapCompose(str.strip, 
                                     str.lower, 
                                     remove_commas_from_numbers, 
                                     remove_everything_before_digits),
        output_processor = TakeFirst()
    )
    ingredients = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    attr_dict = Field(
        input_processor = MapCompose(strip_list_or_dict),
        output_processor = TakeFirst()
    )
    ga_dict = Field(
        input_processor = MapCompose(strip_list_or_dict),
        output_processor = TakeFirst()
    )
    pass
