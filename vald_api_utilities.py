import requests
import gzip
from io import StringIO
import csv
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt

def format_date_to_iso8601(date):

    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:23] + "Z"

def post_call(url,data=None):
    if data != None:
        response = requests.post(url, data=data)
    else:
        response = requests.post(url)
    if response.status_code == 200:
        # Parse the JSON response to get the token
        return response
    else:
        print(f"Failed to obtain token. Status Code: {response.status_code}, Response: {response.text}")
        return ''
    
def get_call(url,header,parameters=None,):
    if parameters != None:
        for key,val in parameters.items():
            url = url+key+val
    response = requests.get(url,headers=header)
    if response.status_code == 200:
        # Print the response from the API
        return response
    else:
        print(f"Failed to retrieve tenants. Status Code: {response.status_code}")
        return ''

class vald_api:
    def __init__(self,client_id,client_secret,tenant_id=None,region='USA'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        if region =='USA':
            self.tenant_url = 'https://prd-use-api-externaltenants.valdperformance.com'
            self.profile_url = 'https://prd-use-api-externalprofile.valdperformance.com'
        elif region == 'Australia':
            self.tenant_url = 'https://prd-aue-api-externaltenants.valdperformance.com'
            self.profile_url = 'https://prd-aue-api-externalprofile.valdperformance.com'
        elif region == 'Europe':
            self.tenant_url = 'https://prd-euw-api-externaltenants.valdperformance.com'
            self.profile_url = 'https://prd-euw-api-externalprofile.valdperformance.com'
        else:
            print('Entered region not one of the available three options (USA/Australia/Europe).')

    # Get the access token
    def get_token(self,url='https://security.valdperformance.com/connect/token'):
        payload = {
        'grant_type': 'client_credentials',
        'client_id': self.client_id,
        'client_secret': self.client_secret
        }   
        response = post_call(url,data=payload)
        if response == '':
            pass
        else:
            self.token = response.json().get('access_token')
            self.header = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
    def get_all_tenants(self):
        parameters = {
            '/tenants':'',
        }
        response = get_call(self.tenant_url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.tenants = response.json()['tenants']

    def get_tenant_info(self, tenant_id = None):
        if self.tenant_id != None:
            parameters ={
                '/tenants/':self.tenant_id
            }
            response = get_call(self.tenant_url,self.header,parameters=parameters)
            if response == '':
                pass
            else:
                self.tenant_info = response.json()
        elif tenant_id != None:
            self.tenant_id = tenant_id
            parameters ={
                '/':self.tenant_id
            }
            response = get_call(self.tenant_url,self.header,parameters=parameters)
            if response == '':
                pass
            else:
                self.tenant_info = response.json()
        else:
            print('No tenant ID found. Please provide a tenant ID.')
    def get_tenant_categories(self):
        if self.tenant_id != None:
            parameters = {
                '/categories':'',
                '?TenantId=':self.tenant_id,
            }
            response = get_call(self.tenant_url,self.header,parameters=parameters)
            if response == '':
                pass
            else:
                self.categories_df = pd.DataFrame(response.json()['categories'])
        else:
            print('No tenant ID found. Please provide a tenant ID using "get_tenant_info()".')

    def get_tenant_groups(self):
        if self.tenant_id != None:
            parameters = {
                '/groups':'',
                '?TenantId=':self.tenant_id,
            }
            response = get_call(self.tenant_url,self.header,parameters=parameters)
            if response == '':
                pass
            else:
                self.groups_df = pd.DataFrame(response.json()['groups'])
        else:
            print('No tenant ID found. Please provide a tenant ID using "get_tenant_info()".')

    def get_group_profiles(self,group_name,category_name='Team')    :
        cat_id = self.categories_df.loc[self.categories_df['name']==category_name,'id'].values[0]
        parameters = {
            '/profiles':'',
            '?TenantId=':self.tenant_id,
            '&GroupId=':self.groups_df.loc[(self.groups_df['name']==group_name)&(self.groups_df['categoryId']==cat_id),'id'].values[0],
        }
        response = get_call(self.profile_url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.profile_df = pd.DataFrame(response.json()['profiles'])


