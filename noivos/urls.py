from django.urls import path
from . import views

urlpatterns = [
 path('', views.home, name='home'),
 path('lista_convidados', views.lista_convidados, name='lista_convidados'),
 path('exportar_convidados_excel/', views.exportar_convidados_excel, name='exportar_convidados_excel'),
 path('excluir_presente/<int:presente_id>/', views.excluir_presente, name='excluir_presente'),
 path('convidado/excluir/<int:convidado_id>/', views.excluir_convidado, name='excluir_convidado'),
 path('cadastrar_convidados_em_lote/', views.cadastrar_convidados_em_lote, name='cadastrar_convidados_em_lote'),

 
]
