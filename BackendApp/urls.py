from django.urls import path
from BackendApp.views import *

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('teachers/', teacher_list, name='teacher_list'),
    path('subjects/', subject_list, name='subject_list'),
    path('classes/', class_list, name='class_list'),
    path('timetable/', timetable_view, name='timetable_view'),
    path('adjustment/', adjustment_today, name='adjustment_today'),
    path('add_dummy_data/', add_dummy_data, name='add_dummy_data'),

    
    path('teachers/', teacher_list, name='teacher-list'),
    path('teachers/create/', create_teacher, name='teacher-create'),
    path('teachers/update/<int:pk>/', update_teacher, name='teacher-update'),
    path('teachers/delete/<int:pk>/', delete_teacher, name='teacher-delete'),
] 