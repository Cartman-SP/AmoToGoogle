from amokey import *
import requests
import datetime

headers = {
    'Authorization': f'Bearer {long_term_token}',
    'Content-Type': 'application/json'
}

burl = 'https://amoteamdemo.amocrm.ru/'

def timestamp(timestamp):
    try:
        return datetime.datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')
    except Exception as e:
        return 'Незавершенна'
def get_pipelines():
    response = requests.get(f'{burl}api/v4/leads/pipelines', headers=headers)
    return response.json()['_embedded']['pipelines']

def get_pipelines_names(pipelines):
    result = []
    for i in pipelines:
        result.append(i['name'])
    return result

def which_pipeline(pipelines,id):
    for i in pipelines:
        if(i['id']==id):
            return i['name']
        
def which_status(pipelines,pipelinesid,id):
    for i in pipelines:
        if(i['id']==pipelinesid):
            for j in i['_embedded']['statuses']:
                if(j['id']==id):
                    return j['name']

def get_persons():
    response = requests.get(f'{burl}api/v4/users',headers=headers)
    return response.json()['_embedded']['users']

def which_person(persons,id):
    for i in persons:
        if(i['id']==id):
            return i['name']

def convert_custom_fields(fields,custom_fields,name):
    result = []
    if(fields):
        for field in fields:
            custom_fields[name].add(field['field_name'])
            result.append(field ['values'][0]['value'])
    return {'result':result,'custom_fields':custom_fields}

def get_data():
    pipelines = get_pipelines()
    pipelines_names = get_pipelines_names(pipelines)

    persons = get_persons()
    leads = []
    page = 1
    while True:
        try:
            params = {
                'page':page,
                'with':'catalog_elements'
            }
            url = f'{burl}api/v4/leads'
            response = requests.get(url, headers=headers,params=params)
            buff_leads = response.json()['_embedded']['leads']
            leads.extend(buff_leads)
            page+=1
        except Exception as e:
            break
    formated_leads = []
    custom_fields = {}
    for i in pipelines_names:
        custom_fields[i]=set()
    for i in leads:
        formated_lead=[]    
        formated_lead.append(i['id'])
        formated_lead.append(which_person(persons,i['responsible_user_id']))
        formated_lead.append(which_status(pipelines,i['pipeline_id'],i['status_id']))
        formated_lead.append(which_pipeline(pipelines,i['pipeline_id']))
        formated_lead.append(i['price'])
        formated_lead.append(timestamp(i['created_at']))
        formated_lead.append( timestamp(i['closed_at']))
        data = convert_custom_fields(i['custom_fields_values'],custom_fields,formated_lead[3])
        custom_fields = data['custom_fields']
        formated_lead.extend(data['result'])
        formated_leads.append(formated_lead)
    return {'names':pipelines_names,'leads':formated_leads,'custom_fields':custom_fields}
