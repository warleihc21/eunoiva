from asyncio import constants
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from noivos.models import Convidados, Presentes, Acompanhante


def convidados(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presentes = Presentes.objects.filter(reservado=False).order_by('-importancia')
    return render(request, 'convidados.html', {'convidado': convidado, 'presentes': presentes, 'token': token})

def responder_presenca(request):
    resposta = request.GET.get('resposta')
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)

    if resposta not in ['C', 'R']:
        messages.error(request, 'Você deve confirmar ou recusar')
        return redirect(f"{reverse('convidados')}?token={token}")
    
    convidado.status = resposta
    convidado.save()

    return redirect(f"{reverse('convidados')}?token={token}")

def reservar_presente(request, id):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presente = get_object_or_404(Presentes, id=id)

    presente.reservado = True
    presente.reservado_por = convidado
    presente.save()
    return redirect(f'{reverse('convidados')}?token={token}')

def adicionar_acompanhante(request, token):
    convidado = get_object_or_404(Convidados, token=token)

    if request.method == 'POST':
        nome_acompanhante = request.POST.get('nome')

        # Verifica se o limite de acompanhantes foi atingido
        if convidado.acompanhantes_count() >= convidado.maximo_acompanhantes:
            return HttpResponseForbidden("Você já atingiu o número máximo de acompanhantes permitidos.")

        # Adiciona o novo acompanhante
        Acompanhante.objects.create(nome=nome_acompanhante, convidado=convidado)
        return redirect(f"{reverse('convidados')}?token={token}")  # Redireciona para a página do convidado

    # Renderiza a página do convidado com os acompanhantes existentes
    presentes = Presentes.objects.all()
    return render(request, 'convidados.html', {'convidado': convidado, 'presentes': presentes})
