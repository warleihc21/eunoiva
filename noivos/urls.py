from django.urls import path
from . import views

urlpatterns = [
 path('', views.home, name='home'),
 path('lista_convidados', views.lista_convidados, name='lista_convidados'),
 path('exportar_convidados_excel/', views.exportar_convidados_excel, name='exportar_convidados_excel'),
 path('excluir_presente/<int:presente_id>/', views.excluir_presente, name='excluir_presente'),
 path('convidado/excluir/<int:convidado_id>/', views.excluir_convidado, name='excluir_convidado'),
 path('cadastrar_convidados_em_lote/', views.cadastrar_convidados_em_lote, name='cadastrar_convidados_em_lote'),
 path('salvar-mensagem/', views.salvar_mensagem, name='salvar_mensagem'),
 path('enviar-mensagens/', views.enviar_mensagens, name='enviar_mensagens'),
 path('substituir_imagem/', views.substituir_imagem, name='substituir_imagem'),
 path('substituir_imagem_noivos/', views.substituir_imagem_noivos, name='substituir_imagem_noivos'),
 path('editar_mensagem/', views.editar_mensagem, name='editar_mensagem'),
 path("buscar_produto/", views.buscar_detalhes_produto, name="buscar_produto"),
 path('excluir-imagem-galeria/', views.excluir_imagem_galeria, name='excluir_imagem_galeria'),
 path('admin_produto/', views.admin_produto, name='admin_produto'),
 path('importar_lista_padrao/', views.importar_lista_padrao, name='importar_lista_padrao'),
 path('editar_produto_base/<int:produto_id>/', views.editar_produto_base, name='editar_produto_base'),
 path('desativar_produto_base/<int:produto_id>/', views.desativar_produto_base, name='desativar_produto_base'),
 path('selecionar-presentes/', views.selecionar_presentes_prontos, name='selecionar_presentes_prontos'),

 
]
