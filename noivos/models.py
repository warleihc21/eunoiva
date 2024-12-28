from io import BytesIO
from django.forms import ValidationError
from django.urls import reverse
import secrets
from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_primeiro_conjuge = models.CharField(max_length=100, blank=True, null=True)  # Primeiro cônjuge
    nome_segundo_conjuge = models.CharField(max_length=100, blank=True, null=True)  # Segundo cônjuge
    data_casamento = models.DateField(blank=True, null=True)
    imagem = models.ImageField(upload_to='imagens_perfil/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    mensagem_noivos = models.TextField(blank=True, null=True)


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

    @property  # Adicione este decorador
    def link_convite(self):
        return f'http://127.0.0.1:8000{reverse("convidados")}?token={self.token}'

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
    nome_presente = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='presentes/', blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    importancia = models.IntegerField()
    reservado = models.BooleanField(default=False)
    reservado_por = models.ForeignKey('Convidados', null=True, blank=True, on_delete=models.SET_NULL)
    link_sugestao_compra = models.URLField(max_length=500, blank=True, null=True)
    link_cobranca = models.URLField(max_length=500, blank=True, null=True)

    def clean(self):
        # Validar links longos
        if self.link_sugestao_compra and len(self.link_sugestao_compra) > 500:
            raise ValidationError("O link de sugestão é muito longo.")
        if self.link_cobranca and len(self.link_cobranca) > 500:
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
    

