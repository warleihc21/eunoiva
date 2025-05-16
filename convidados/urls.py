from django.urls import path
from . import views

urlpatterns = [
    path('', views.convidados, name='convidados'),
    path('responder_presenca/', views.responder_presenca, name='responder_presenca'),
    path('reservar_presente/<int:id>', views.reservar_presente, name='reservar_presente'),
    path('convidado/<str:token>/', views.adicionar_acompanhante, 
    name='adicionar_acompanhante'),
    path('excluir-acompanhante/<str:token>/<int:acompanhante_id>/', views.excluir_acompanhante, name='excluir_acompanhante'),
    path('cancelar_reserva/<int:presente_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('mensagem-aos-noivos/', views.mensagem_aos_noivos, name='mensagem_aos_noivos'),
    path('excluir-mensagem/', views.excluir_mensagem, name='excluir_mensagem'),
]