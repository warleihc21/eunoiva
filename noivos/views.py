import pandas as pd
import csv
import openpyxl
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .models import Convidados, Presentes
from django.contrib.auth.decorators import login_required # type: ignore
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render
import logging


@login_required(login_url='/auth/logar/')
def home(request):
    if request.method == "GET":
        presentes = Presentes.objects.all()
        nao_reservado = Presentes.objects.filter(reservado=False).count()
        reservado = Presentes.objects.filter(reservado=True).count()

        presentes_reservados = Presentes.objects.filter(reservado=True)
        total_reservado = sum(presente.preco for presente in presentes_reservados)

        data = [nao_reservado, reservado]
        return render(request, 'home.html', {
            'presentes': presentes,
            'data': data,
            'presentes_reservados': presentes_reservados,
            'total_reservado': total_reservado
        })

    elif request.method == "POST":
        nome_presente = request.POST.get('nome_presente')
        foto = request.FILES.get('foto')
        preco = request.POST.get('preco')
        link_sugestao_compra = request.POST.get('link_sugestao_compra')
        link_cobranca = request.POST.get('link_cobranca')  # Novo campo
        if ',' in preco:
            preco = preco.replace(',', '.')
        preco = float(preco)

        importancia = int(request.POST.get('importancia'))
        if importancia < 1 or importancia > 5:
            return redirect('home')

        presentes = Presentes(
            nome_presente=nome_presente,
            foto=foto,
            preco=preco,
            importancia=importancia,
            link_sugestao_compra=link_sugestao_compra,
            link_cobranca=link_cobranca,  # Salva o link
        )
        presentes.save()

    return redirect('home')
   


def lista_convidados(request):
   if request.method == 'GET':
      convidados = Convidados.objects.all()
      return render(request, 'lista_convidados.html', {'convidados': convidados})
   elif request.method == 'POST':
      nome_convidado = request.POST.get('nome_convidado')
      whatsapp = request.POST.get('whatsapp')
      maximo_acompanhantes = int(request.POST.get('maximo_acompanhantes', 0))
      convidados = Convidados(
      nome_convidado=nome_convidado,
      whatsapp=whatsapp,
      maximo_acompanhantes=maximo_acompanhantes
   )
   convidados.save()
   return redirect('lista_convidados')


def exportar_convidados_excel(request):
    # Criar um novo arquivo Excel
    wb = openpyxl.Workbook()

    # Planilha para confirmados
    ws_confirmados = wb.create_sheet('Confirmados')
    
    # Adicionar os títulos das colunas
    ws_confirmados.append(['Convidado', 'Whatsapp', 'Acompanhante', 'Link', 'Status'])
    
    # Obter convidados confirmados
    convidados_confirmados = Convidados.objects.filter(status='C')

    for convidado in convidados_confirmados:
        for acompanhante in convidado.acompanhantes.all():
            # Adicionar uma linha para cada acompanhante
            ws_confirmados.append([convidado.nome_convidado, convidado.whatsapp, acompanhante.nome, convidado.link_convite, convidado.get_status_display()])
    
    # Planilha para aguardando confirmação
    ws_aguardando = wb.create_sheet('Aguardando confirmação')
    
    # Adicionar os títulos das colunas
    ws_aguardando.append(['Convidado', 'Whatsapp', 'Máximo de acompanhantes', 'Link', 'Status'])
    
    # Obter convidados aguardando confirmação
    convidados_aguardando = Convidados.objects.filter(status='AC')

    for convidado in convidados_aguardando:
        ws_aguardando.append([convidado.nome_convidado, convidado.whatsapp, convidado.maximo_acompanhantes, convidado.link_convite, convidado.get_status_display()])

    # Remover a planilha padrão que é criada automaticamente
    del wb['Sheet']

    # Definir a resposta HTTP para o arquivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=convidados.xlsx'

    # Salvar o arquivo Excel na resposta HTTP
    wb.save(response)
    return response


def excluir_presente(request, presente_id):
    presente = get_object_or_404(Presentes, id=presente_id)
    presente.delete()
    return redirect('home')

def excluir_convidado(request, convidado_id):
    # Tentar pegar o convidado com o ID fornecido, se não encontrar, gerar um erro 404
    convidado = get_object_or_404(Convidados, id=convidado_id)
    
    # Excluir o convidado
    convidado.delete()
    
    # Exibir uma mensagem de sucesso
    messages.success(request, f'O convidado {convidado.nome_convidado} foi excluído com sucesso.')
    
    # Redirecionar para a lista de convidados (ou qualquer página que você queira)
    return redirect('lista_convidados')  # Substitua 'lista_convidados' pela URL da sua página de lista