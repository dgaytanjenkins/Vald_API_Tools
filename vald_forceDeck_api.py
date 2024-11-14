import requests
import gzip
from io import StringIO
import csv
import re
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt

import vald_api_utilities as vau

class forceDecks_api:
    def __init__(self,tenant_id,header,region='USA'):
        self.tenant_id = tenant_id
        self.header = header
        if region =='USA':
            self.url = 'https://prd-use-api-extforcedecks.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-extforcedecks.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-extforcedecks.valdperformance.com'
        else:
            print('Entered region not one of the available three options (USA/Australia/Europe).')
        parameters = {
            '/resultdefinitions':'',
        }
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.result_def_df = pd.DataFrame(response.json()['resultDefinitions'])

    def get_single_result_definition(self,result_id):
        parameters = {
            '/resultdefinitions/':result_id,
        }
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.result_def = response.json()

    def get_tests_info(self,date,profile_id=None,pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$"):
        if isinstance(date,datetime):
            pass
        elif isinstance(date,str) and re.match(pattern, date):
            date = datetime.strptime(date, "%d/%m/%Y")
        else:
            print('Date does not match format - dd/mm/yyyy, ie 01/01/1900')
        if profile_id != None:
            parameters = {
                '/tests':'',
                '?TenantId=':self.tenant_id,
                '&ModifiedFromUtc=':vau.format_date_to_iso8601(date).replace(':','%3A'),
                '&ProfileId=':profile_id,
            }
        else:
            parameters = {
            '?TenantId=':self.tenant_id,
            '&ModifiedFromUtc=':vau.format_date_to_iso8601(date).replace(':','%3A'),
            }
    
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.tests_df = pd.DataFrame(response.json()['tests'])

    def get_test_results(self,test_id):
        parameters = {
            '/v2019q3/':'',
            'teams/':self.tenant_id,
            '/tests/':test_id,
            '/trials':'',
        }
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            df = pd.DataFrame(response.json()[0]['results'])
            def_df = pd.DataFrame(list(df['definition'].values))
            df = df.drop(columns=['definition'])
            df['rep'] = 1
            for key,val in response.json()[0].items():
                if key == 'results':
                    pass
                else:
                    df[key] = val
            if len(response.json()) > 1:
                for rep, entry in enumerate(response.json()[1:]):
                    temp_df = pd.DataFrame(entry['results']).drop(columns=['definition'])
                    temp_df['rep'] = rep+2
                    for key,val in entry.items():
                        if key == 'results':
                            pass
                        else:
                            temp_df[key] = val
                    df = pd.concat([df, temp_df])
            df.rename(columns={"id": "testId"},inplace=True)
            self.results_df = pd.merge(df,def_df,how='left',left_on='resultId',right_on='id')
        
    def get_force_trace(self,test_id,):
        parameters = {
            '/v2019q3/':'',
            'teams/':self.tenant_id,
            '/tests/':test_id,
            '/recording/file':'',
        }
        response = vau.get_call(self.url,self.header,parameters=parameters)          
        if response == '':
            pass
        else:
            compressed_data = response.content
            decompressed_data = gzip.decompress(compressed_data)
            decoded_text = decompressed_data.decode('utf-8')
            cleaned_text = '\n'.join(decoded_text.splitlines()[2:])
            self.raw_df = pd.read_csv(StringIO(cleaned_text))
            self.raw_df['test_id'] = test_id