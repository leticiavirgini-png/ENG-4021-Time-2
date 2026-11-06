"""
URL configuration for MeuSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from MeuSite import views 

urlpatterns = [
    path("admin/", admin.site.urls),

    path('', views.home, name='home'),



    path('Artigos/', views.Artigos, name='Artigos'), 

    path('ComoUsar/', views.ComoUsar, name='ComoUsar'), 
    
    path('ConsentimentoDados/', views.ConsentimentoDados, name='ConsentimentoDados'),
    path('CriarConta/', views.CriarConta, name='CriarConta'), 
    
    path(
        'EdicaoUsuario/<int:usuario_id>/',
        views.EdicaoUsuario,
        name='EdicaoUsuario'
    ),
    
    path('EsqueciSenha/', views.EsqueciSenha, name='EsqueciSenha'), 
    
    path('PreferenciasNotificacoes/', views.PreferenciasNotificacoes, name='PreferenciasNotificacoes'),
    
    path(
        'RemocaoUsuario/<int:usuario_id>/',
        views.RemocaoUsuario,
        name='RemocaoUsuario'
    ),
    
    path('login/', views.Tela, name='Login'),
    path('Tela/', views.Tela, name='Tela'), 

    path('HistoricoFamiliar/', views.HistoricoFamiliar, name='HistoricoFamiliar' ),

    path('CheckupInteligente/', views.CheckupInteligente, name='CheckupInteligente'),
   
    path('ListarUsuarios/',views.ListarUsuarios, name='ListarUsuarios' ),

    path('CalendarioCuidados/', views.CalendarioCuidados, name='CalendarioCuidados'),

    path('RelatorioPreventivo/', views.RelatorioPreventivo, name='RelatorioPreventivo'),
   
    path('Familiares/', views.Familiares, name='Familiares'),
    
    path('PerfilSaude/', views.PerfilSaude, name='PerfilSaude'),
    path('CadastroCuidados/', views.CadastroCuidados, name='CadastroCuidados'),

    path('InicioLogado/', views.InicioLogado, name='InicioLogado'),
]
