"""
URL configuration for aibot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/health/', views.api_health, name='api_health'),
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),
    path('api/strategies/', views.api_strategies, name='api_strategies'),
    path('api/strategy/create/', views.api_strategy_create, name='api_strategy_create'),
    path('api/settings/exchange/', views.api_settings_exchange, name='api_settings_exchange'),
    path('api/settings/exchange/get/', views.api_settings_exchange_get, name='api_settings_exchange_get'),
    path('api/settings/ai/', views.api_settings_ai, name='api_settings_ai'),
    path('api/settings/ai/get/', views.api_settings_ai_get, name='api_settings_ai_get'),
    
    # Prompt API endpoints
    path('api/prompts/', views.api_prompts_list, name='api_prompts_list'),
    path('api/prompt/<str:prompt_name>/', views.api_prompt_get, name='api_prompt_get'),
    path('api/prompt/', views.api_prompt_save, name='api_prompt_save'),
    path('api/prompt/<str:prompt_name>/delete/', views.api_prompt_delete, name='api_prompt_delete'),
    
    # Plans API endpoints
    path('api/plans/', views.api_plans_list, name='api_plans_list'),
    path('api/plan/create/', views.api_plan_create, name='api_plan_create'),
]

# 开发模式下提供静态文件和媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
