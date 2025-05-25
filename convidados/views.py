from asyncio import constants
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.urls import reverse
from noivos.models import Convidados, ImagemNoivos, MensagemAosNoivos, MensagemSobreNoivoNoiva, Perfil, Presentes, Acompanhante
from datetime import datetime
from django.views.decorators.http import require_POST


def convidados(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presentes = Presentes.objects.filter(user=convidado.user).order_by('-importancia')
    presentes = sorted(presentes, key=lambda p: p.reservado)

    # Recuperando o perfil do usuário
    perfil = Perfil.objects.get(user=convidado.user)

    # Recuperando as imagens dos noivos filtrando pelo perfil
    imagem_noiva = ImagemNoivos.objects.filter(perfil=perfil, tipo='noiva').first()
    imagem_noivo = ImagemNoivos.objects.filter(perfil=perfil, tipo='noivo').first()

    # Recuperando as mensagens
    mensagem_noiva = MensagemSobreNoivoNoiva.objects.filter(perfil=perfil, tipo='noiva').first()
    mensagem_noivo = MensagemSobreNoivoNoiva.objects.filter(perfil=perfil, tipo='noivo').first()

    mensagens_enviadas = MensagemAosNoivos.objects.filter(user=convidado.user).order_by('-data_envio')

    timestamp = int(datetime.now().timestamp())

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
        'mensagem_noivo': mensagem_noivo,
        'mensagens_enviadas': mensagens_enviadas,
    })

def responder_presenca(request):
    resposta = request.GET.get('resposta')
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)

    if resposta not in ['C', 'R']:
        messages.error(request, 'Você deve confirmar ou recusar')
        # Redireciona para a seção de confirmação de presença
        return redirect(f"{reverse('convidados')}?token={token}#confirmacao-presenca")
    
    convidado.status = resposta
    convidado.save()

    # Redireciona para a seção de confirmação de presença
    return redirect(f"{reverse('convidados')}?token={token}#confirmacao-presenca")

def reservar_presente(request, id):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presente = get_object_or_404(Presentes, id=id, user=convidado.user)

    presente.reservado = True
    presente.reservado_por = convidado
    presente.save()
    # Redireciona para a seção de presentes
    return redirect(f'{reverse("convidados")}?token={token}#lista-presentes')


def cancelar_reserva(request, presente_id):
    token = request.GET.get('token')
    presente = get_object_or_404(Presentes, id=presente_id)

    if presente.reservado_por and presente.reservado_por.token == token:
        presente.reservado = False
        presente.reservado_por = None
        presente.save()
        messages.success(request, "Reserva cancelada com sucesso.")
    else:
        messages.error(request, "Você não tem permissão para cancelar esta reserva.")

    # Redireciona para a seção de presentes
    return redirect(f'{reverse("convidados")}?token={token}#lista-presentes')

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

    # Redireciona para a seção de confirmação de presença (onde os acompanhantes são adicionados)
    return redirect(f"{reverse('convidados')}?token={token}#confirmacao-presenca")

def excluir_acompanhante(request, token, acompanhante_id):
    convidado = get_object_or_404(Convidados, token=token)
    acompanhante = get_object_or_404(Acompanhante, id=acompanhante_id, convidado=convidado)

    if request.method == 'POST':
        acompanhante.delete()
        messages.success(request, 'Acompanhante excluído com sucesso!')

    # Redireciona para a seção de confirmação de presença
    return redirect(f"{reverse('convidados')}?token={token}#confirmacao-presenca")


def mensagem_aos_noivos(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)

    if request.method == 'POST':
        texto_mensagem = request.POST.get('texto_mensagem')
        mensagem_id = request.POST.get('mensagem_id')
        
        if mensagem_id:
            mensagem = get_object_or_404(MensagemAosNoivos, id=mensagem_id, escrita_por=convidado)
            mensagem.texto_mensagem = texto_mensagem
            mensagem.save()
            messages.success(request, 'Mensagem atualizada com sucesso!')
        elif texto_mensagem:
            MensagemAosNoivos.objects.create(
                user=convidado.user,
                texto_mensagem=texto_mensagem,
                escrita_por=convidado
            )
            messages.success(request, 'Mensagem enviada com sucesso!')
        else:
            messages.error(request, 'A mensagem não pode estar vazia.')

    # Redireciona para a seção de mensagens
    return redirect(f"{reverse('convidados')}?token={token}#mensagem-aos-noivos")

@require_POST
def excluir_mensagem(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    mensagem_id = request.POST.get('mensagem_id')
    
    mensagem = get_object_or_404(MensagemAosNoivos, id=mensagem_id, escrita_por=convidado)
    mensagem.delete()
    
    messages.success(request, 'Mensagem excluída com sucesso!')
    # Redireciona para a seção de mensagens
    return redirect(f"{reverse('convidados')}?token={token}#mensagem-aos-noivos")