from asyncio import constants
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from noivos.models import Convidados, ImagemNoivos, MensagemSobreNoivoNoiva, Perfil, Presentes, Acompanhante
from datetime import datetime


def convidados(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presentes = Presentes.objects.filter(user=convidado.user).order_by('-importancia')
    # Ordenando: primeiro os não reservados, depois os reservados
    presentes = sorted(presentes, key=lambda p: p.reservado)


    # Recuperando as imagens dos noivos
    imagem_noiva = ImagemNoivos.objects.filter(tipo='noiva').first()
    imagem_noivo = ImagemNoivos.objects.filter(tipo='noivo').first()

    # Recuperando as mensagens
    mensagem_noiva = MensagemSobreNoivoNoiva.objects.filter(tipo='noiva').first()  # Ajuste conforme a lógica que você tem para mensagens
    mensagem_noivo = MensagemSobreNoivoNoiva.objects.filter(tipo='noivo').first()  # Ajuste conforme a lógica que você tem para mensagens

    timestamp = int(datetime.now().timestamp())

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
        'timestamp': timestamp,
        'imagem_noiva': imagem_noiva,
        'imagem_noivo': imagem_noivo,
        'mensagem_noiva': mensagem_noiva,
        'mensagem_noivo': mensagem_noivo
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


def cancelar_reserva(request, presente_id):
    convidado_token = request.GET.get('token')
    presente = get_object_or_404(Presentes, id=presente_id)
    
    # Corrigindo a comparação para o campo correto
    if presente.reservado_por and presente.reservado_por.token == convidado_token:
        presente.reservado = False
        presente.reservado_por = None  # Deve setar como None o usuário que fez a reserva
        presente.save()
        messages.success(request, "Reserva cancelada com sucesso.")
    else:
        messages.error(request, "Você não tem permissão para cancelar esta reserva.")
    
    return redirect('lista_presentes')

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
