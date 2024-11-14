import requests
import gzip
from io import StringIO
import csv
import re
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt

import vald_api_utilities as vau

class nordBoard_api:
    def __init__(self,tenant_id,header,region='USA'):
        self.tenant_id = tenant_id
        self.header = header
        if region =='USA':
            self.url = 'https://prd-use-api-externalnordbord.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-externalnordbord.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-externalnordbord.valdperformance.com'
        else:
            print('Entered region not one of the available three options (USA/Australia/Europe).')
        
    def get_multiple_tests(self,start_date,stop_date,modified_date=None,profileID=None,pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$"):
        if isinstance(start_date,datetime):
            pass
        elif isinstance(start_date,str) and re.match(pattern, start_date):
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
        else:
            print('Start date does not match format - dd/mm/yyyy, ie 01/01/1900')
        if isinstance(stop_date,datetime):
            pass
        elif isinstance(stop_date,str) and re.match(pattern, stop_date):
            stop_date = datetime.strptime(stop_date, "%d/%m/%Y")
        else:
            print('Stop date does not match format - dd/mm/yyyy, ie 01/01/1900')

        assert (stop_date-start_date).days < 180, 'Submitted start and stop date is greater than 180 days apart.'

        if modified_date != None:
            if isinstance(modified_date,datetime):
                pass
            elif isinstance(modified_date,str) and re.match(pattern, modified_date):
                modified_date = datetime.strptime(modified_date, "%d/%m/%Y")
            else:
                print('Modified date does not match format - dd/mm/yyyy, ie 01/01/1900')
            parameters = {
                '/tests':'',
                '?TenantId=':self.tenant_id,
                '&ModifiedFromUtc=':vau.format_date_to_iso8601(modified_date.replace(hour=5)).replace(':','%3A'),
            }
        else:
            parameters = {
                '/tests':'',
                '?TenantId=':self.tenant_id,
                '&ModifiedFromUtc=':vau.format_date_to_iso8601(start_date.replace(hour=5)).replace(':','%3A'), 
            }
        parameters['&TestFromUtc=']=vau.format_date_to_iso8601(start_date.replace(hour=5)).replace(':','%3A')
        parameters['&TestToUtc=']=vau.format_date_to_iso8601(stop_date.replace(hour=20)).replace(':','%3A')
        if profileID != None:
            parameters['&AthleteId=']=profileID
        parameters['&Page=']='1'
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.tests_df = pd.DataFrame(response.json()['tests'])
            if response.json()['pageCount'] > response.json()['page']:
                for pageNum in range(response.json()['page']+1,response.json()['pageCount']+1):
                    parameters['&Page='] = str(pageNum)
                    response = vau.get_call(self.url,self.header,parameters=parameters)
                    if response == '':
                        pass
                    else:
                        temp_df = pd.DataFrame(response.json()['tests'])
                        self.tests_df = pd.concat([self.tests_df,temp_df])
    def get_test_results(self,test_id):
        parameters = {
            '/tests':'',
            '/':test_id,
            '?TenantId=':self.tenant_id,
        }
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.test = response.json()
    def get_force_trace(self, test_id):
        parameters = {
            '/tests':'',
            '/':test_id,
            '/forceframetrace':'',
            '?TenantId=':self.tenant_id,
        }
        response = vau.get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.raw = response.json()
            self.raw['forces'] = pd.DataFrame(response.json()['forces'])
    