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
        presentes = Presentes.objects.filter(user=request.user)
        nao_reservado = presentes.filter(reservado=False).count()
        reservado = presentes.filter(reservado=True).count()

        presentes_reservados = presentes.filter(reservado=True)
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

        Presentes.objects.create(
            user=request.user,
            nome_presente=nome_presente,
            foto=foto,
            preco=preco,
            importancia=importancia,
            link_sugestao_compra=link_sugestao_compra,
            link_cobranca=link_cobranca,
        )
    return redirect('home')
   


def lista_convidados(request):
    if request.method == 'GET':
        convidados = Convidados.objects.filter(user=request.user)
        return render(request, 'lista_convidados.html', {'convidados': convidados})
    elif request.method == 'POST':
        nome_convidado = request.POST.get('nome_convidado')
        whatsapp = request.POST.get('whatsapp')
        maximo_acompanhantes = int(request.POST.get('maximo_acompanhantes', 0))
        Convidados.objects.create(
            user=request.user,
            nome_convidado=nome_convidado,
            whatsapp=whatsapp,
            maximo_acompanhantes=maximo_acompanhantes
        )
        return redirect('lista_convidados')


def cadastrar_convidados_em_lote(request):
    if request.method == 'POST':
        arquivo = request.FILES.get('arquivo_convidados')
        if not arquivo:
            messages.error(request, "Nenhum arquivo foi enviado.")
            return redirect('lista_convidados')

        try:
            # Detecta o tipo de arquivo (CSV ou Excel)
            if arquivo.name.endswith('.csv'):
                df = pd.read_csv(arquivo)
            elif arquivo.name.endswith('.xlsx'):
                df = pd.read_excel(arquivo)
            else:
                messages.error(request, "Formato de arquivo não suportado. Envie um arquivo CSV ou Excel.")
                return redirect('lista_convidados')

            # Verifica se as colunas necessárias estão presentes
            colunas_esperadas = ['Nome do convidado', 'Whatsapp', 'Máximo de Acompanhantes']
            if not all(coluna in df.columns for coluna in colunas_esperadas):
                messages.error(request, f"O arquivo deve conter as colunas: {', '.join(colunas_esperadas)}.")
                return redirect('lista_convidados')

            # Itera pelas linhas e cria os convidados
            for _, row in df.iterrows():
                Convidados.objects.create(
                    user=request.user,
                    nome_convidado=row['Nome do convidado'],
                    whatsapp=str(row['Whatsapp']),
                    maximo_acompanhantes=int(row['Máximo de Acompanhantes'])
                )

            messages.success(request, "Convidados cadastrados com sucesso!")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao processar o arquivo: {str(e)}")
        return redirect('lista_convidados')


def exportar_convidados_excel(request):
    # Criar um novo arquivo Excel
    wb = openpyxl.Workbook()

    # Filtrar os convidados do usuário autenticado
    usuario_responsavel = request.user

    # Planilha para confirmados
    ws_confirmados = wb.create_sheet('Confirmados')
    # Adicionar os títulos das colunas
    ws_confirmados.append(['Convidado', 'Whatsapp', 'Acompanhante', 'Link', 'Status'])
    # Obter convidados confirmados do usuário responsável
    convidados_confirmados = Convidados.objects.filter(user=usuario_responsavel, status='C')

    for convidado in convidados_confirmados:
        for acompanhante in convidado.acompanhantes.all():
            # Adicionar uma linha para cada acompanhante
            ws_confirmados.append([
                convidado.nome_convidado, 
                convidado.whatsapp, 
                acompanhante.nome, 
                convidado.link_convite, 
                convidado.get_status_display()
            ])

    # Planilha para aguardando confirmação
    ws_aguardando = wb.create_sheet('Aguardando confirmação')
    # Adicionar os títulos das colunas
    ws_aguardando.append(['Convidado', 'Whatsapp', 'Máximo de acompanhantes', 'Link', 'Status'])
    # Obter convidados aguardando confirmação do usuário responsável
    convidados_aguardando = Convidados.objects.filter(user=usuario_responsavel, status='AC')

    for convidado in convidados_aguardando:
        ws_aguardando.append([
            convidado.nome_convidado, 
            convidado.whatsapp, 
            convidado.maximo_acompanhantes, 
            convidado.link_convite, 
            convidado.get_status_display()
        ])

    # Planilha para total de confirmados (incluindo acompanhantes)
    ws_total_confirmados = wb.create_sheet('Total Confirmados')
    # Adicionar os títulos das colunas
    ws_total_confirmados.append(['Nome', 'Whatsapp', 'Tipo'])
    # Inicializar contador para o total de pessoas
    total_pessoas = 0

    for convidado in convidados_confirmados:
        # Adicionar o convidado à lista
        ws_total_confirmados.append([convidado.nome_convidado, convidado.whatsapp, 'Convidado'])
        total_pessoas += 1

        # Adicionar os acompanhantes do convidado à lista
        for acompanhante in convidado.acompanhantes.all():
            ws_total_confirmados.append([acompanhante.nome, '', 'Acompanhante'])  # Deixe o WhatsApp vazio para acompanhantes
            total_pessoas += 1

    # Adicionar o total de pessoas no final da planilha
    ws_total_confirmados.append([])
    ws_total_confirmados.append(['Total de pessoas:', '', total_pessoas])

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
    convidado = get_object_or_404(Convidados, id=convidado_id, user=request.user)
    convidado.delete()
    messages.success(request, f'O convidado {convidado.nome_convidado} foi excluído.')
    return redirect('lista_convidados')

