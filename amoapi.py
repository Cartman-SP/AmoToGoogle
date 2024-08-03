import requests
from datetime import datetime

# Глобальные переменные
burl = 'https://amoteamdemo.amocrm.ru/'
headers = {}

def update_global_settings(amo_url, long_term_token):
    global burl, headers
    burl = amo_url
    headers = {
        'Authorization': f'Bearer {long_term_token}',
        'Content-Type': 'application/json'
    }

def timestamp(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')
    except Exception as e:
        return 'Незавершенна'

def get_pipelines():
    response = requests.get(f'{burl}api/v4/leads/pipelines', headers=headers)
    return response.json()['_embedded']['pipelines']

def get_pipelines_names(pipelines):
    return [i['name'] for i in pipelines]

def which_pipeline(pipelines, id):
    for i in pipelines:
        if i['id'] == id:
            return i['name']

def which_status(pipelines, pipelinesid, id):
    for i in pipelines:
        if i['id'] == pipelinesid:
            for j in i['_embedded']['statuses']:
                if j['id'] == id:
                    return j['name']

def get_persons():
    response = requests.get(f'{burl}api/v4/users', headers=headers)
    return response.json()['_embedded']['users']

def which_person(persons, id):
    for i in persons:
        if i['id'] == id:
            return i['name']

def convert_custom_fields(fields, custom_fields, name):
    result = []
    if fields:
        for field in fields:
            custom_fields[name].add(field['field_name'])
            result.append(field['values'][0]['value'])
    return {'result': result, 'custom_fields': custom_fields}

def get_tasks():
    tasks = []
    page = 1
    while True:
        try:
            params = {'page': page}
            url = f'{burl}api/v4/tasks'
            response = requests.get(url, headers=headers, params=params)
            buff_tasks = response.json()['_embedded']['tasks']
            tasks.extend(buff_tasks)
            page += 1
        except Exception as e:
            break
    return tasks

def which_task(id, tasks):
    for i in tasks:
        if i['id'] == id:
            return i

def get_data(amo_url, long_term_token):
    update_global_settings(amo_url, long_term_token)
    pipelines = get_pipelines()
    pipelines_names = get_pipelines_names(pipelines)
    persons = get_persons()
    leads = []
    page = 1
    while True:
        try:
            params = {'page': page, 'with': 'catalog_elements'}
            url = f'{burl}api/v4/leads'
            response = requests.get(url, headers=headers, params=params)
            buff_leads = response.json()['_embedded']['leads']
            leads.extend(buff_leads)
            page += 1
        except Exception as e:
            break
    formated_leads = []
    custom_fields = {name: set() for name in pipelines_names}
    for i in leads:
        formated_lead = []
        formated_lead.append(i['id'])
        formated_lead.append(which_person(persons, i['responsible_user_id']))
        formated_lead.append(which_status(pipelines, i['pipeline_id'], i['status_id']))
        formated_lead.append(which_pipeline(pipelines, i['pipeline_id']))
        formated_lead.append(i['price'])
        formated_lead.append(timestamp(i['created_at']))
        formated_lead.append(timestamp(i['closed_at']))
        data = convert_custom_fields(i['custom_fields_values'], custom_fields, formated_lead[3])
        custom_fields = data['custom_fields']
        formated_lead.extend(data['result'])
        formated_leads.append(formated_lead)
    return {'names': pipelines_names, 'leads': formated_leads, 'custom_fields': custom_fields}

def timestamp_to_time(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_date = dt_object.strftime("%d.%m.%Y %H:%M")
    return formatted_date

def get_events():
    events = []
    page = 1
    event_types = [
        'contact_added',
        'incoming_call',
        'entity_responsible_changed',
        'outgoing_call',
        'incoming_chat_message',
        'outgoing_chat_message',
        'lead_added',
        'lead_status_changed',
        'task_completed',
        'task_added'
    ]
    while True:
        try:
            params = {'page': page, 'with': 'contact_name,lead_name'}
            for i, event_type in enumerate(event_types):
                params[f'filter[type][{i}]'] = event_type
            url = f'{burl}api/v4/events'
            response = requests.get(url, headers=headers, params=params)
            buff_events = response.json()['_embedded']['events']
            events.extend(buff_events)
            page += 1
            print(page)
        except Exception as e:
            break
    return events

def write_events_to_file(events, filename='events.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for event in events:
            file.write(str(event) + '\n')

def get_values(obj, persons, pipelines, tasks):
    if obj['type'] == 'contact_added':
        data = []
        data.extend(obj['value_before'])
        data.extend(obj['value_after'])
        return data
    elif obj['type'] in ['incoming_call', 'outgoing_call']:
        return ['', '']
    elif obj['type'] == 'entity_responsible_changed':
        before = obj['value_before']
        after = obj['value_after']
        bef_user = 'Робот' if before[0]['responsible_user']['id'] == 0 else which_person(persons, before[0]['responsible_user']['id'])
        af_user = 'Робот' if after[0]['responsible_user']['id'] == 0 else which_person(persons, after[0]['responsible_user']['id'])
        return [bef_user, af_user]
    elif obj['type'] in ['incoming_chat_message', 'outgoing_chat_message']:
        return ['', obj['value_after'][0]['message']['id']]
    elif obj['type'] == 'lead_added':
        return ['', '']
    elif obj['type'] == 'lead_status_changed':
        before = obj['value_before'][0]['lead_status']
        after = obj['value_after'][0]['lead_status']
        return [
            which_status(pipelines, before['pipeline_id'], before['id']),
            which_status(pipelines, after['pipeline_id'], after['id'])
        ]
    elif obj['type'] == 'task_completed':
        return [
            which_task(obj['entity_id'], tasks)['text'],
            which_task(obj['entity_id'], tasks)['result']['text']
        ]
    elif obj['type'] == 'task_added':
        return ['', which_task(obj['entity_id'], tasks)['text']]

translate = {
    'contact_added': 'Новый контакт',
    'incoming_call': 'Входящий звонок',
    'entity_responsible_changed': 'Ответственный изменен',
    'outgoing_call': 'Исходящий звонок',
    'incoming_chat_message': 'Входящее сообщение',
    'outgoing_chat_message': 'Исходящее сообщение',
    'lead_added': 'Новая сделка',
    'lead_status_changed': 'Изменение этапа продаж',
    'task_completed': 'Завершение задачи',
    'task_added': 'Новая задача'
}

objects = {
    'contact_added': 'Контакт',
    'incoming_call': 'Звонок',
    'entity_responsible_changed': 'Сделка',
    'outgoing_call': 'Звонок',
    'incoming_chat_message': 'Беседа',
    'outgoing_chat_message': 'Беседа',
    'lead_added': 'Сделка',
    'lead_status_changed': 'Сделка',
    'task_completed': 'Задача',
    'task_added': 'Задача'
}

def get_data2(amo_url, long_term_token):
    update_global_settings(amo_url, long_term_token)
    persons = get_persons()
    pipelines = get_pipelines()
    tasks = get_tasks()
    events = get_events()
    write_events_to_file(events, 'formatted_events.txt')
    result = []
    print(events)
    for i in events:
        buff = []
        buff.append(timestamp_to_time(i['created_at']))  #Дата
        if(i['created_by']==0):
            buff.append('Робот')
        else:
            buff.append(which_person(persons,i['created_by']))   #Автор
        buff.append(objects[i['type']])                          #Объект
        if(i['type']=='incoming_chat_message' or i['type']=='outgoing_chat_message'):
            buff.append('A'+str(i['value_after'][0]['message']['talk_id']))
        elif(i['type']=='task_completed' or i['type']=='task_added'):
            buff.append('Задание №'+str(i['entity_id']))
        else:
            buff.append(events[5]['_embedded']['entity']['name'])       #Название
        buff.append(translate[i['type']])                               #Событие
        buff.extend(get_values(i,persons,pipelines,tasks))              #Значение до Значение после
        result.append(buff)
        print(buff)
    return {'result':result}



