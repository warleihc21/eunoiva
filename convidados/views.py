from asyncio import constants
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from noivos.models import Convidados, Presentes, Acompanhante


def convidados(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presentes = Presentes.objects.filter(reservado=False, user=convidado.user).order_by('-importancia')

    # Verificar se o convidado pode adicionar acompanhantes
    if convidado.maximo_acompanhantes > 0:
        acompanhantes_restantes = convidado.maximo_acompanhantes - convidado.acompanhantes_count()
    else:
        acompanhantes_restantes = 0

    return render(request, 'convidados.html', {
        'convidado': convidado,
        'presentes': presentes,
        'token': token,
        'acompanhantes_restantes': acompanhantes_restantes,
    })

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
    presente = get_object_or_404(Presentes, id=id, user=convidado.user)

    presente.reservado = True
    presente.reservado_por = convidado
    presente.save()
    return redirect(f'{reverse('convidados')}?token={token}')

def adicionar_acompanhante(request, token):
    convidado = get_object_or_404(Convidados, token=token)
    
    if request.method == 'POST' and convidado.acompanhantes_count() < convidado.maximo_acompanhantes:
        nome = request.POST.get('nome')
        if nome:
            Acompanhante.objects.create(convidado=convidado, nome=nome)
            messages.success(request, 'Acompanhante adicionado com sucesso!')
        else:
            messages.error(request, 'O nome do acompanhante é obrigatório.')
    else:
        messages.error(request, 'Você já atingiu o limite máximo de acompanhantes.')

    return redirect(f"{reverse('convidados')}?token={token}")

def excluir_acompanhante(request, token, acompanhante_id):
    convidado = get_object_or_404(Convidados, token=token)
    acompanhante = get_object_or_404(Acompanhante, id=acompanhante_id, convidado=convidado)

    if request.method == 'POST':
        acompanhante.delete()
        messages.success(request, 'Acompanhante excluído com sucesso!')

    return redirect(f"{reverse('convidados')}?token={token}")
