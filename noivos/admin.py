from django.contrib import admin
from .models import MensagemAosNoivos, Presentes, Convidados, Perfil, MensagemPersonalizada

admin.site.register(Presentes)
admin.site.register(Convidados)
admin.site.register(Perfil)
admin.site.register(MensagemPersonalizada)
admin.site.register(MensagemAosNoivos)
