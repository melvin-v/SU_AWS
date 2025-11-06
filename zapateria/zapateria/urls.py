from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth de Django (login, logout, reset, etc.)
    # Esto crea rutas /accounts/login/ y /accounts/logout/
    path('accounts/', include('django.contrib.auth.urls')),

    # Tu app
    path('', include('app.urls')),
     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
