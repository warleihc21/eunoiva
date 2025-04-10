from django.contrib import admin
from .models import MensagemAosNoivos, Presentes, Convidados, Perfil, MensagemPersonalizada, Acompanhante, MensagemSobreNoivoNoiva, ImagemNoivos, ImagemGaleria

admin.site.register(Presentes)
admin.site.register(Convidados)
admin.site.register(Perfil)
admin.site.register(MensagemPersonalizada)
admin.site.register(MensagemAosNoivos)
admin.site.register(Acompanhante)
admin.site.register(MensagemSobreNoivoNoiva)
admin.site.register(ImagemNoivos)
admin.site.register(ImagemGaleria)

