from io import BytesIO

from urllib.parse import quote
from django.forms import ValidationError
from django.urls import reverse
import secrets
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from ckeditor.fields import RichTextField

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_primeiro_conjuge = models.CharField(max_length=100, blank=True, null=True)
    nome_segundo_conjuge = models.CharField(max_length=100, blank=True, null=True)
    data_casamento = models.DateField(blank=True, null=True)
    horario_casamento = models.TimeField(blank=True, null=True)  # Novo campo para horário do casamento
    imagem = models.ImageField(upload_to='imagens_perfil/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    mensagem_noivos = models.TextField(
        blank=True,
        null=True,
        default="O grande dia está chegando e estamos cheios de alegria por poder compartilhar com nossa família e amigos um dos momentos mais especiais de nossas vidas! Será um dia repleto de amor, diversão e muita emoção, e queremos muito contar com sua presença para tornar essa celebração ainda mais inesquecível. Vamos comemorar juntos e criar memórias que ficarão para sempre em nossos corações!"
    )

    configurado = models.BooleanField(default=False)

    # Campos de endereço
    cep = models.CharField(max_length=10, blank=True, null=True)
    rua = models.CharField(max_length=150, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=50, default='Brasil')
    estado = models.CharField(max_length=2, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
class ImagemGaleria(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='galeria')
    imagem = models.ImageField(upload_to='imagems_galeria/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    

    def __str__(self):
        return f"Imagem de {self.perfil.user.username}"
    
class ImagemNoivos(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, related_name='fotosnoivos')
    imagem = models.ImageField(upload_to='imagems_noivos/', validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    tipo = models.CharField(max_length=10, choices=[('noiva', 'Noiva'), ('noivo', 'Noivo')])

    def __str__(self):
        return f"Imagem de {self.tipo} de {self.perfil.user.username}"

    
class MensagemSobreNoivoNoiva(models.Model):
    perfil = models.ForeignKey('Perfil', on_delete=models.CASCADE, related_name='mensagens')
    tipo = models.CharField(max_length=10, choices=[('noiva', 'Noiva'), ('noivo', 'Noivo')])
    mensagem = models.TextField(blank=True)

    MENSAGEM_PADRAO_NOIVA = (
        "Ela é a luz que ilumina todos ao seu redor, com um sorriso capaz de derreter qualquer coração. Sua beleza, inteligência e graça são apenas algumas das suas qualidades, mas é o seu coração generoso e a paciência com o noivo que realmente a definem. Ela é, sem dúvida, a pessoa mais incrível que você vai conhecer – e todos nós torcemos para que ele saiba o quanto ela merece ser amada a cada dia."
    )

    MENSAGEM_PADRAO_NOIVO = (
        "Ele é o mestre das piadas, sempre pronto para fazer todos rirem, mesmo nas situações mais inesperadas. Com um coração enorme e o talento de fazer a noiva sorrir até nos momentos mais sérios, ele é a verdadeira prova de que o amor existe. Mesmo sendo um pouco desastrado (quem nunca derrubou algo em um jantar de família?), ele traz leveza e diversão a cada momento. Ele pode não ser perfeito, mas é perfeito para ela – e é isso que realmente importa."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Define valores padrão ao inicializar uma nova instância
        if not self.pk:  # Se for um novo registro
            if self.tipo == 'noiva' and not self.mensagem:
                self.mensagem = self.MENSAGEM_PADRAO_NOIVA
            elif self.tipo == 'noivo' and not self.mensagem:
                self.mensagem = self.MENSAGEM_PADRAO_NOIVO

    def __str__(self):
        return f"Mensagem de {self.tipo} de {self.perfil.user.username}"

# Modelo para armazenar mensagens personalizadas
class MensagemPersonalizada(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_personalizadas')
    mensagem = models.TextField()
    imagem = models.FileField(upload_to='mensagens_imagens/', null=True, blank=True)  # Campo para imagem
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.user.username}"
   
class Convidados(models.Model):
    status_choices = (
        ('AC', 'Aguardando confirmação'),
        ('C', 'Confirmado'),
        ('R', 'Recusado')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convidados')
    nome_convidado = models.CharField(max_length=100, null=True)
    whatsapp = models.CharField(max_length=25, null=True, blank=True)
    maximo_acompanhantes = models.PositiveIntegerField(default=0, null=True)
    token = models.CharField(max_length=25)
    status = models.CharField(max_length=2, choices=status_choices, default='AC')

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(16)
               
        super(Convidados, self).save(*args, **kwargs)

    @property
    def link_convite(self):
        return f'https://inoivos.site{reverse("convidados")}?token={self.token}'

    def __str__(self):
        return self.nome_convidado

    def acompanhantes_count(self):
        return self.acompanhantes.count()
    
    
class Acompanhante(models.Model):
    nome = models.CharField(max_length=100)
    convidado = models.ForeignKey(Convidados, related_name='acompanhantes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome} (Acompanhante de {self.convidado.nome_convidado})"

def __str__(self):
    return self.nome_convidado


class Presentes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='presentes')
    nome_presente = models.CharField(max_length=1000)
    foto = models.ImageField(upload_to='presentes/', blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    importancia = models.IntegerField()
    reservado = models.BooleanField(default=False)
    reservado_por = models.ForeignKey('Convidados', null=True, blank=True, on_delete=models.SET_NULL)
    link_sugestao_compra = models.URLField(max_length=1000, blank=True, null=True)
    link_cobranca = models.URLField(max_length=500, blank=True, null=True)

    def clean(self):
        # Validar links longos
        if self.link_sugestao_compra and len(self.link_sugestao_compra) > 1000:
            raise ValidationError("O link de sugestão é muito longo.")
        if self.link_cobranca and len(self.link_cobranca) > 1000:
            raise ValidationError("O link de cobrança é muito longo.")

    def save(self, *args, **kwargs):
        # Ajustar a imagem para formato quadrado com fundo branco
        if self.foto:
            img = Image.open(self.foto)
            img = img.convert("RGB")  # Garantir que a imagem seja RGB
            
            # Redimensionar mantendo proporção, com fundo branco
            desired_size = 300
            img = ImageOps.pad(img, (desired_size, desired_size), method=Image.Resampling.LANCZOS, color=(255, 255, 255))
            
            # Salvar a imagem ajustada
            buffer = BytesIO()
            img.save(buffer, format='JPEG')  # Salvar no formato JPEG
            buffer.seek(0)
            self.foto = ContentFile(buffer.read(), name=self.foto.name)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_presente
    

class MensagemAosNoivos(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensagens_aos_noivos')
    texto_mensagem = RichTextField()  # Substitua o TextField por RichTextField
    escrita_por = models.ForeignKey('Convidados', null=True, blank=True, on_delete=models.SET_NULL)
    data_envio = models.DateTimeField(auto_now_add=True)  # Data de envio automática

    def __str__(self):
        return f"Mensagem de {self.escrita_por.nome_convidado} para {self.user.username}"
