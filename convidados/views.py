from asyncio import constants
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
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
        return JsonResponse({'success': False, 'message': 'Você deve confirmar ou recusar'}, status=400)

    convidado.status = resposta
    convidado.save()

    if resposta == 'C':
        mensagem = 'Presença confirmada! Estamos ansiosos para vê-lo no nosso casamento!'
    else:
        mensagem = 'Presença recusada. Sentiremos sua falta, esperamos vê-lo em outra oportunidade!'

    return JsonResponse({'success': True, 'status': resposta, 'message': mensagem})

def reservar_presente(request, id):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    presente = get_object_or_404(Presentes, id=id, user=convidado.user)

    presente.reservado = True
    presente.reservado_por = convidado
    presente.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Presente reservado com sucesso!',
            'presente_id': presente.id,
            'token': token
        })
    return redirect(f'{reverse("convidados")}?token={token}#lista-presentes')


def cancelar_reserva(request, presente_id):
    token = request.GET.get('token')
    presente = get_object_or_404(Presentes, id=presente_id)

    if presente.reservado_por and presente.reservado_por.token == token:
        presente.reservado = False
        presente.reservado_por = None
        presente.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Reserva cancelada com sucesso.',
                'presente_id': presente.id
            })
        messages.success(request, "Reserva cancelada com sucesso.")
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para cancelar esta reserva.'
            })
        messages.error(request, "Você não tem permissão para cancelar esta reserva.")

    return redirect(f'{reverse("convidados")}?token={token}#lista-presentes')


def adicionar_acompanhante(request, token): 
    convidado = get_object_or_404(Convidados, token=token)

    if request.method == 'POST' and convidado.acompanhantes_count() < convidado.maximo_acompanhantes:
        nome = request.POST.get('nome')
        if nome:
            acompanhante = Acompanhante.objects.create(convidado=convidado, nome=nome)
            return JsonResponse({
                'success': True,
                'message': 'Acompanhante adicionado com sucesso!',
                'acompanhante': {
                    'id': acompanhante.id,
                    'nome': acompanhante.nome
                },
                'acompanhantes_restantes': convidado.maximo_acompanhantes - convidado.acompanhantes_count()
            })
        else:
            return JsonResponse({'success': False, 'message': 'O nome do acompanhante é obrigatório.'})
    return JsonResponse({'success': False, 'message': 'Limite de acompanhantes atingido.'})


def excluir_acompanhante(request, token, acompanhante_id):
    convidado = get_object_or_404(Convidados, token=token)
    acompanhante = get_object_or_404(Acompanhante, id=acompanhante_id, convidado=convidado)

    if request.method == 'POST':
        acompanhante.delete()
        return JsonResponse({
            'success': True,
            'message': 'Acompanhante excluído com sucesso!',
            'acompanhantes_restantes': convidado.maximo_acompanhantes - convidado.acompanhantes_count()
        })
    
    return JsonResponse({'success': False, 'message': 'Erro ao excluir acompanhante.'})


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
            return JsonResponse({
                'success': True,
                'message': 'Mensagem atualizada com sucesso!',
                'mensagem': {
                    'id': mensagem.id,
                    'texto_mensagem': mensagem.texto_mensagem
                }
            })
        elif texto_mensagem:
            mensagem = MensagemAosNoivos.objects.create(
                user=convidado.user,
                texto_mensagem=texto_mensagem,
                escrita_por=convidado
            )
            return JsonResponse({
                'success': True,
                'message': 'Mensagem enviada com sucesso!',
                'mensagem': {
                    'id': mensagem.id,
                    'texto_mensagem': mensagem.texto_mensagem
                }
            })
        else:
            return JsonResponse({'success': False, 'message': 'A mensagem não pode estar vazia.'})

    return JsonResponse({'success': False, 'message': 'Método inválido.'})


@require_POST
def excluir_mensagem(request):
    token = request.GET.get('token')
    convidado = get_object_or_404(Convidados, token=token)
    mensagem_id = request.POST.get('mensagem_id')

    mensagem = get_object_or_404(MensagemAosNoivos, id=mensagem_id, escrita_por=convidado)
    mensagem.delete()

    return JsonResponse({'success': True, 'message': 'Mensagem excluída com sucesso!'})