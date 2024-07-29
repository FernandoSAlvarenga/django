"""
URL configuration for fernando project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from main import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('menu/', views.menu, name='menu'),
    path('pedido/<int:pizza_id>/', views.pedido_pizza, name='pedido_pizza'),
    path('pedidos_cliente/', views.pedidos_cliente, name='pedidos_cliente'),
    path('pedidos_admin/', views.pedidos_admin, name='pedidos_admin'),
    path('editar_cliente/<int:user_id>/', views.editar_cliente, name='editar_cliente'),
    path('excluir_cliente/<int:user_id>/', views.excluir_cliente, name='excluir_cliente'),
]

if settings.DEBUG:
    urlpatterns += [
        path('static/<path:path>/', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    ]

