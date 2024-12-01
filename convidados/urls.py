from django.urls import path
from . import views

urlpatterns = [
    path('', views.convidados, name='convidados'),
    path('responder_presenca/', views.responder_presenca, name='responder_presenca'),
    path('reservar_presente/<int:id>', views.reservar_presente, name='reservar_presente'),
    path('convidado/<str:token>/', views.adicionar_acompanhante, 
    name='adicionar_acompanhante'),
    path('excluir-acompanhante/<str:token>/<int:acompanhante_id>/', views.excluir_acompanhante, name='excluir_acompanhante'),
]