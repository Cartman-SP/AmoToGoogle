from django.shortcuts import render
from .models import AmoAcc
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
import json
from django.views.decorators.http import require_GET
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests

@login_required  # Декоратор требует аутентификации
def main(request):
    return render(request, 'index.html')

def login_redirect(request):
    # Перенаправляем на страницу входа
    return redirect('admin:index')  # Можно перенаправить на страницу входа админки



def main(request):
    return render(request, 'index.html')

@require_POST
def create_amo(request):
    # Получаем данные из запроса
    data = json.loads(request.body)
    name = data.get('name')
    google_link = data.get('google_link')
    long_term_token = data.get('long_term_token')

    lead_filter = data.get('lead_filter')
    if(not(lead_filter)):
        lead_filter = 'No'
    event_filter = data.get('event_filter')

    # Проверяем, что все поля заполнены
    if not all([name, google_link, long_term_token, lead_filter, event_filter]):
        return JsonResponse({'status': 'error', 'message': 'Все поля должны быть заполнены'}, status=400)

    # Создаем новый объект
    amo_acc = AmoAcc(
        name=name,
        google_link=google_link,
        long_term_token=long_term_token,
        lead_filter=lead_filter,
        event_filter=event_filter
    )
    amo_acc.save()

    return JsonResponse({'status': 'success', 'message': 'Данные успешно сохранены'})

def options(burl,long_term_roken):
    headers = {
        'Authorization': f'Bearer {long_term_roken}',
        'Content-Type': 'application/json'
    } 
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
    option = []
    for i in leads:
        if(i['custom_fields_values']):
            for j in i['custom_fields_values']:
                option.append(j['field_name'])
    return option

@require_GET
def get_options(request):
    name = request.GET.get('name')
    long_term_token = request.GET.get('long_term_token')
    arr = options(name,long_term_token)
    return JsonResponse({'options': arr})