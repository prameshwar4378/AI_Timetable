"""
URL configuration for AI_TIMETABLE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from Backend import urls as backend_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('software/', include(backend_urls)),
    path('dumm__data', backend_urls.add_dummy_data, name='add_dummy_data'),
    path('fake_generate_school_timetable', backend_urls.generate_timetable_view, name='fake_generate_school_timetable'),
    path('generate-timetable/', backend_urls.generate_timetable_view, name='generate_timetable'),

]
