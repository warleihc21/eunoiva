from django.shortcuts import render
from django.http import HttpResponse
from .utils import password_is_valid, email_html
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from noivos.models import ImagemGaleria, ImagemNoivos, MensagemSobreNoivoNoiva, Perfil
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth
import os
from django.conf import settings
from .models import Ativacao
from hashlib import sha256
from django.contrib.auth.decorators import login_required




def cadastro(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')
        email = request.POST.get('email')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect('/auth/cadastro')

        if User.objects.filter(username=username).exists():
            messages.add_message(request, constants.ERROR, 'Usuário já existente')
            return redirect('/auth/cadastro')

        if User.objects.filter(email=email).exists():
            messages.add_message(request, constants.ERROR, 'E-mail já cadastrado')
            return redirect('/auth/cadastro')

        try:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            password=senha,
                                            is_active=False)
            user.save()

            token = sha256(f"{username}{email}".encode()).hexdigest()
            ativacao = Ativacao(token=token, user=user)
            ativacao.save()

            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            email_html(
                path_template,
                'Cadastro confirmado',
                [email],
                username=username,
                link_ativacao=f"https://www.inoivos.site/auth/ativar_conta/{token}"
            )

            messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado com sucesso! Acesse seu email para validar o seu acesso')
            return redirect('/auth/logar')
        
        except Exception as e:
            print("Erro no cadastro:", e)
            messages.add_message(request, constants.ERROR, 'Erro interno do sistema')
            return redirect('/auth/cadastro')


def logar(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'logar.html')
    elif request.method == "POST":
        username = request.POST.get('usuario')
        senha = request.POST.get('senha')

        usuario = auth.authenticate(username=username, password=senha)

        if not usuario:
            messages.add_message(request, constants.ERROR, 'Username ou senha inválidos')
            return redirect('/auth/logar')
        else:
            auth.login(request, usuario)

            # Verificar se o perfil está configurado
            perfil, created = Perfil.objects.get_or_create(user=usuario)
            if not perfil.configurado:
                return redirect('/auth/configurar_perfil')

            return redirect('/noivos/')
            

def sair(request):
    auth.logout(request)
    return redirect('/auth/logar')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Essa token já foi usado')
        return redirect('/auth/logar')

    user = User.objects.get(username=token.user.username)
    user.is_active = True
    user.save()

    token.ativo = True
    token.save()

    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')


@login_required(login_url='/auth/logar/')
def configurar_perfil(request):
    # Obtém o perfil do usuário logado
    perfil, created = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Campos do perfil
        nome_primeiro_conjuge = request.POST.get('nome_primeiro_conjuge')
        nome_segundo_conjuge = request.POST.get('nome_segundo_conjuge')
        data_casamento = request.POST.get('data_casamento')
        horario_casamento = request.POST.get('horario_casamento')
        mensagem_noivos = request.POST.get('mensagem_noivos')

        # Campos do endereço
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        numero = request.POST.get('numero')
        complemento = request.POST.get('complemento')
        bairro = request.POST.get('bairro')
        pais = request.POST.get('pais')
        estado = request.POST.get('estado')
        municipio = request.POST.get('municipio')

        # Verificar se os campos obrigatórios foram preenchidos
        if not nome_primeiro_conjuge or not nome_segundo_conjuge or not data_casamento or not cep or not rua or not numero or not bairro or not estado or not municipio:
            messages.error(request, "Preencha todos os campos obrigatórios.")
            return redirect('/auth/configurar_perfil')

        # Atualizar o perfil
        perfil.nome_primeiro_conjuge = nome_primeiro_conjuge
        perfil.nome_segundo_conjuge = nome_segundo_conjuge
        perfil.data_casamento = data_casamento
        perfil.horario_casamento = horario_casamento
        perfil.mensagem_noivos = mensagem_noivos
        perfil.cep = cep
        perfil.rua = rua
        perfil.numero = numero
        perfil.complemento = complemento
        perfil.bairro = bairro
        perfil.pais = pais
        perfil.estado = estado
        perfil.municipio = municipio
        perfil.configurado = True

        if 'imagem' in request.FILES:
            perfil.imagem = request.FILES['imagem']

        perfil.save()

        # Verifica se o perfil já tem mensagens cadastradas
        if not perfil.mensagens.exists():
            MensagemSobreNoivoNoiva.objects.create(
                perfil=perfil,
                tipo='noiva',
                mensagem='Ela é a luz que ilumina todos ao seu redor, com um sorriso capaz de derreter qualquer coração. Sua beleza, inteligência e graça são apenas algumas das suas qualidades, mas é o seu coração generoso e a paciência com o noivo que realmente a definem. Ela é, sem dúvida, a pessoa mais incrível que você vai conhecer – e todos nós torcemos para que ele saiba o quanto ela merece ser amada a cada dia.'
            )
            MensagemSobreNoivoNoiva.objects.create(
                perfil=perfil,
                tipo='noivo',
                mensagem='Ele é o mestre das piadas, sempre pronto para fazer todos rirem, mesmo nas situações mais inesperadas. Com um coração enorme e o talento de fazer a noiva sorrir até nos momentos mais sérios, ele é a verdadeira prova de que o amor existe. Mesmo sendo um pouco desastrado (quem nunca derrubou algo em um jantar de família?), ele traz leveza e diversão a cada momento. Ele pode não ser perfeito, mas é perfeito para ela – e é isso que realmente importa.'
            )

        # Salvar múltiplas imagens da galeria
        imagens = request.FILES.getlist('galeria_imagens')
        for imagem in imagens:
            ImagemGaleria.objects.create(perfil=perfil, imagem=imagem)

        # Processar imagens e mensagens dos noivos
        imagem_noiva = request.FILES.get('imagem_noiva')
        imagem_noivo = request.FILES.get('imagem_noivo')
        mensagem_noiva = request.POST.get('mensagem_noiva', '').strip()
        mensagem_noivo = request.POST.get('mensagem_noivo', '').strip()

        # Atualizar imagem da noiva
        if imagem_noiva:
            imagem_noiva_obj = ImagemNoivos.objects.filter(perfil=perfil, tipo='noiva').first()
            if imagem_noiva_obj:
                imagem_noiva_obj.imagem = imagem_noiva
                imagem_noiva_obj.save()
            else:
                ImagemNoivos.objects.create(perfil=perfil, tipo='noiva', imagem=imagem_noiva)

        # Atualizar imagem do noivo
        if imagem_noivo:
            imagem_noivo_obj = ImagemNoivos.objects.filter(perfil=perfil, tipo='noivo').first()
            if imagem_noivo_obj:
                imagem_noivo_obj.imagem = imagem_noivo
                imagem_noivo_obj.save()
            else:
                ImagemNoivos.objects.create(perfil=perfil, tipo='noivo', imagem=imagem_noivo)

        # Atualizar mensagem da noiva
        if mensagem_noiva:
            mensagem_noiva_obj = perfil.mensagens.filter(tipo='noiva').first()
            if mensagem_noiva_obj:
                mensagem_noiva_obj.mensagem = mensagem_noiva
                mensagem_noiva_obj.save()
            else:
                MensagemSobreNoivoNoiva.objects.create(perfil=perfil, tipo='noiva', mensagem=mensagem_noiva)

        # Atualizar mensagem do noivo
        if mensagem_noivo:
            mensagem_noivo_obj = perfil.mensagens.filter(tipo='noivo').first()
            if mensagem_noivo_obj:
                mensagem_noivo_obj.mensagem = mensagem_noivo
                mensagem_noivo_obj.save()
            else:
                MensagemSobreNoivoNoiva.objects.create(perfil=perfil, tipo='noivo', mensagem=mensagem_noivo)

        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('/noivos/')

    # Passa o perfil para o template
    context = {
        'perfil': perfil,
    }
    
    # Adiciona as mensagens e imagens dos noivos ao contexto, se existirem
    if hasattr(perfil, 'mensagens'):
        mensagem_noiva = perfil.mensagens.filter(tipo='noiva').first()
        mensagem_noivo = perfil.mensagens.filter(tipo='noivo').first()
        
        if mensagem_noiva:
            context['mensagem_noiva'] = mensagem_noiva.mensagem
        if mensagem_noivo:
            context['mensagem_noivo'] = mensagem_noivo.mensagem
    
    if hasattr(perfil, 'fotosnoivos'):
        imagem_noiva = perfil.fotosnoivos.filter(tipo='noiva').first()
        imagem_noivo = perfil.fotosnoivos.filter(tipo='noivo').first()
        
        if imagem_noiva:
            context['imagem_noiva'] = imagem_noiva
        if imagem_noivo:
            context['imagem_noivo'] = imagem_noivo
    
    return render(request, 'configurar_perfil.html', context)




def index(request):
    if request.user.is_authenticated:
        return redirect('/noivos/')
    else:
        return redirect('/auth/logar/')




