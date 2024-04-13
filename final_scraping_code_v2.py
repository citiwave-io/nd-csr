#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import urllib.request
import re
import sys
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup as bs
import cloudscraper
import datetime
import schedule
import time
import datetime

import os
import selenium
# ft
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
import sys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys

import hashlib

base_link = "https://nextdoor.com/"


# In[2]:


# ft
def headless_browser():
    """ this function initiates the driver """
    
    test_ua = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'
    
    options = FirefoxOptions()
    
#     activete "headless" to make the driver hidden
#     options.add_argument("--headless")
    options.add_argument("-private-window")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--window-size=1920,1080")
#     options.add_argument(f'--user-agent={test_ua}')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")

    driver = webdriver.Firefox(options=options)
    
    return driver

driver = headless_browser()


# In[2]:


def get_soup(url , browser_based = False):
    
    global driver
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'cache-control': 'max-age=0',
        'dnt': '1',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
     
    if not browser_based:
        response = requests.get( url,
            headers=headers,
            )
        soup = bs(response.text , "lxml")
        status_code = response.status_code
        
    else:
        driver.get(url)
        time.sleep(5)
        soup = bs( driver.page_source , "lxml")
        status_code = 200 if driver.current_url == url  else 600
        
    
    
    print(status_code)
    
    return soup , status_code


# In[3]:


def get_data_neighborhood(neighnorhood_soup , neighnorhood_url , neighborhood , city_state_data_dict):
    
    """ parse the soup to get all the needed data for the neighborhood"""
    
    j = json.loads(neighnorhood_soup.select("#__NEXT_DATA__")[0].text)
    main_data_part = j["props"]["pageProps"]["apolloState"]["ROOT_QUERY"]
    needed_key = [k for k in list(main_data_part.keys()) if "seoNeighborhood" in k and "city" in k and "neighborhood" in k and "state" in k ][0]
    data_part = main_data_part[needed_key]

    all_statistics_data = data_part["neighborhoodStats"]
    
    resid_count = all_statistics_data["residentsCount"]
    avg_age = all_statistics_data["averageAge"]
    perc_home_owners = all_statistics_data["percentageHomeowners"]
    avg_income = all_statistics_data["averageIncome"]
    description = all_statistics_data["description"]
    
    all_data_neighborhood = {
                            "Neighborhood" : neighborhood,
                            "Neighborhood Residents" : resid_count , 
                            "Neighborhood Home Owners" : perc_home_owners,
                            "Neighborhood Average Age" : avg_age ,
                            "Neighborhood Average Income" : avg_income ,
                            "Neighborhood Description" : description,
                            "Neighborhood Link" : neighnorhood_url,
                            } | city_state_data_dict
    
#     print(all_data_neighborhood)
    return all_data_neighborhood


# In[ ]:





# In[4]:


def get_all_states_data(main_link_all_states):
    """ make the main request for all states """
    
    main_soup_states = get_soup(main_link_all_states)[0]

    state_data = [{"state_link" : element.get("href") , "state_name" : element.text } for element in main_soup_states.select("div.hood_group > p > a.link")]
    
    return state_data


# In[5]:


def get_all_cities_data(main_link_state):
    """ make the main request for all states """
    
    main_soup_cities = get_soup(main_link_state)[0]

    cities_data = [{"city_link" : element.get("href") , "city_name" : element.text } for element in main_soup_cities.select("div.hood_group > p > a.link")]
    
    return cities_data


# In[6]:


def scrape_city(soup , state_name , state_link , city_name , city_link):
    
    """ gets all info of city and the links for its nearbu neighborhoods """

    try:
        perc_home_owners = [s for s in soup.select("span") if s.text.strip() =="Homeowners"][0].find_previous_sibling("span").text
    except:
        perc_home_owners = None
        
    try:
        resid_count = [s for s in soup.select("span") if s.text.strip() =="Residents"][0].find_previous_sibling("span").text
    except:
        resid_count = None
        
    try:
        avg_age = [s for s in soup.select("span") if s.text.strip() =="Average age"][0].find_previous_sibling("span").text
    except:
        avg_age = None
        
    try:
        avg_income = [s for s in soup.select("span") if s.text.strip() =="Average income"][0].find_previous_sibling("span").text
    except:
        avg_income = None
        
    try:
        description = soup.select("meta[name='description']")[0].get("content")
    except:
        description = None
        
    
    try:
        all_neighborhoods_links_elements = [d for d in soup.select("div[class*='Styled_columnGap']") if "Nearby neighborhoods" in d.text][0].select("a")
        all_neighborhoods_data = [{'neighborhood_link' : base_link.strip("/") + element.get("href") , "neighborhood_name" : element.text } for element in all_neighborhoods_links_elements] 
    except:
        all_neighborhoods_data = []
        
    city_state_data_dict = {"State" : state_name , 
                            "State Link" : state_link,
                            "City" : city_name ,
                            "City Link" : city_link,
                            "City Residents" : resid_count , 
                            "City Home Owners" : perc_home_owners,
                            "City Average Age" : avg_age ,
                            "City Average Income" : avg_income ,
                            "City Description" : description }
    
    
    
    return city_state_data_dict , all_neighborhoods_data


# In[7]:


def scrape_city_v2( response , state_name , state_link , city_name , city_link):
    
    """ gets all info of city and the links for its nearby neighborhoods using API requests """

    base_n_link = "https://nextdoor.com/neighborhood/"
    j_data = json.loads(response.text)
#     print(j_data)
    data = j_data["data"]["seoCity"]
    
#     state_name = data["properState"]
#     state_link = "https://nextdoor.com/find-neighborhood/" + state_short_name + "/"
    
    city_slug = city_link.strip(" /").split("/")[-1]
    
    stats = data["cityV2Stats"]
    resid_count = stats["residentsCount"]
    perc_home_owners = stats["percentageHomeowners"]
    avg_age = stats["averageAge"]
    avg_income = stats["averageIncome"]
    description = stats["description"]
    
    
    city_state_data_dict = {"State" : state_name , 
                                "State Link" : state_link,
                                "City" : city_name ,
                                "City Link" : city_link,
                                "City Residents" : resid_count , 
                                "City Home Owners" : perc_home_owners,
                                "City Average Age" : avg_age ,
                                "City Average Income" : avg_income ,
                                "City Description" : description }
    
    
    try:
        all_neighborhoods_data = [{'neighborhood_link' :  base_n_link + n["slug"] + "--" + city_slug + "/", "neighborhood_name" : n["shortName"] } for n in data["cityNeighborhoods"] ]
    except:
        all_neighborhoods_data = []
        
        
    
    return city_state_data_dict , all_neighborhoods_data


# In[35]:


def get_API_creds(driver):
    
    driver.get("https://nextdoor.com/city/girdwood--ak/")
    time.sleep(10)
    all_driver_requests = driver.requests
    
    needed_request = [r for r in all_driver_requests if "nextdoor.com/api/gql/SeoCityQueryV2" in  r.url ][0]
    x_csrftoken = [h for h in dict(needed_request.headers).items() if "x-csrftoken" in h][0][-1]
    sha256Hash = json.loads(needed_request.body)["extensions"]["persistedQuery"]["sha256Hash"]
    
    return  x_csrftoken , sha256Hash


# In[8]:


csrftoken , hash_code =  get_API_creds(driver)

def get_city_soup_api(city_name , state_short_name , hash_code = hash_code , csrftoken =  csrftoken):
    
    cookies = {
        'csrftoken': csrftoken,
    }
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://nextdoor.com',
        'referer': 'https://nextdoor.com/city/kasilof--ak/',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'x-csrftoken': csrftoken,
    }
    
    params = ''
    
    json_data = {
        'operationName': 'SeoCityQueryV2',
        'variables': {
            'input': {
                'city': city_name.strip().lower() ,
                'state': state_short_name.strip().lower() ,
                'country': 'US',
            },
        },
        'extensions': {
            'persistedQuery': {
                'version': 1,
                'sha256Hash': hash_code ,
            },
        },
    }
    
    t1 = time.time()
    response = requests.post(
        'https://nextdoor.com/api/gql/SeoCityQueryV2',
        params=params,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    
    return response , response.status_code


# In[ ]:


def get_all_neighborhoods_from_cities(all_cities_data_df):
    
    all_data_cities = []
    all_data_cities_neighborhoods = []
    
    cities_rows = all_cities_data_df.to_dict(orient = "records")

    for c , city_data in enumerate(cities_rows):
        
        print("------------------")
        print(f"city {c} out of {len(cities_rows)}")
        
        for trial in range(20):
            try:
                
                city_name = city_data["city_name"].strip().lower()
                city_link = city_data["city_link"]
                state_short_name = city_data["state_short_name"]
                state_name = city_data["state_name"]
                state_link = city_data["state_link"]
                print(city_link)
                print(city_name)
                city_response , status = get_city_soup_api(city_name , state_short_name , hash_code = hash_code , csrftoken =  csrftoken)
                print(status)
                
                
                city_state_data_dict , all_neighborhoods_data = scrape_city_v2( city_response , state_name , state_link , city_name , city_link)
                
                city_state_data_df = pd.DataFrame(city_state_data_dict , index = [0]).reset_index(drop = True)
                city_state_data_df["index"] = 0
                
                try:
                    all_neighborhoods_data_df = pd.DataFrame(all_neighborhoods_data).reset_index(drop = True)
                except:
                    all_neighborhoods_data_df = pd.DataFrame(all_neighborhoods_data , index = [0]).reset_index(drop = True)
                    
                    
                all_neighborhoods_data_df["index"] = 0
                
                all_city_df = pd.merge( city_state_data_df , all_neighborhoods_data_df , how = "outer" , on = "index")
        
        
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%5")
                print(f"this city has {len(all_neighborhoods_data)} neighborhoods nearby ")
                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%5")
                all_data_cities.append( city_state_data_df )
                all_data_cities_neighborhoods.append( all_city_df )
                break
            except:
                print("**************")
                print(f"trial of {trial}")
                
                
        
        
        
        
    all_data_cities_only_df = pd.concat(all_data_cities)
    all_data_cities_neighborhoods_df = pd.concat(all_data_cities_neighborhoods)
    
    
    return all_data_cities_only_df , all_data_cities_neighborhoods_df


# In[ ]:


# scrape the data on 2 parts
# part1 : scraping all data of cities 

# run all the iterations 
all_data_neighborhoods = []
all_data_cities = []

main_link_all_states = "https://nextdoor.com/find-neighborhood/"


states_data = get_all_states_data(main_link_all_states)

all_cities_data = []

for state_data in states_data:
    
    state_name = state_data["state_name"]
    state_link = state_data["state_link"]
    state_short_name = state_data["state_link"].strip(" /").split("/")[-1]
    
    print("============================")
    print(state_name)
    print(state_link)
    
    cities_data = get_all_cities_data(state_link)
    
    cities_data_df = pd.DataFrame(cities_data)
    cities_data_df["state_name"] = state_name
    cities_data_df["state_link"] = state_link
    cities_data_df["state_short_name"] = state_short_name
    
    print("**************************************")
    print(f"we have {len(cities_data)}  cities in this state")
    print("**************************************")
    
    all_cities_data.append(cities_data_df)
    
    
all_cities_data_df = pd.concat(all_cities_data)


# In[11]:


all_cities_data_df


# In[30]:


all_data_cities_only_df , all_data_cities_neighborhoods_df = get_all_neighborhoods_from_cities(all_cities_data_df)


# In[34]:


all_data_cities_only_df.shape


# In[12]:


all_data_cities_neighborhoods_df.head()


# In[14]:


all_neigh_data = []


# In[15]:


import concurrent.futures,time

def m_thread(func , urls):
    with concurrent.futures.ThreadPoolExecutor() as executor: # 32 max thread number
        results = executor.map(func, urls)
    return results


# ft


def scrape_neighborhood_m(neighbor_data_indexed ):
    global all_neigh_data 
    
    index , neighbor_data = neighbor_data_indexed
    print("-------------------------------")
    print(index)
    
    
    neighnorhood_url = neighbor_data["neighborhood_link"]
    neighborhood = neighbor_data["neighborhood_name"]
    city_state_data_dict = {key: value for key, value in neighbor_data.items() if "City" in key or "State" in key}
    
    for trial in range(20):
        try:
            neighnorhood_soup = get_soup(neighnorhood_url)[0]                
            
            
            neighborhood_final_data = get_data_neighborhood(neighnorhood_soup = neighnorhood_soup ,
                                                            neighnorhood_url = neighnorhood_url , 
                                                            neighborhood = neighborhood  ,
                                                            city_state_data_dict = city_state_data_dict)
            
            all_neigh_data.append(neighborhood_final_data)
            break
            
        except:
            neighborhood_final_data = {}
            print(f"trial of {trial}")
            None
            
         
    return neighborhood_final_data


# In[18]:


indexed_neighborhood_data_all = enumerate(all_data_cities_neighborhoods_df.to_dict(orient = "records"))
t1 = time.time()
final_list_all_neighborhoods = list(m_thread(scrape_neighborhood_m , indexed_neighborhood_data_all))
final_list_all_neighborhoods
t2 = time.time()
t2 - t1


# In[19]:


all_final_data_df = pd.DataFrame(all_neigh_data).fillna("Not Available")
all_final_data_df.to_csv("data_full_scraping.csv")

