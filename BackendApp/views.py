from django.shortcuts import render,redirect
from .models import *
from django.utils import timezone
from datetime import time



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import Teacher
from .forms import TeacherForm
from .utils import paginated_queryset



def dashboard(request):
    return render(request, 'dashboard.html')



def teacher_list(request):
    """List teachers with pagination."""
    form = TeacherForm()
    rec = Teacher.objects.all().order_by('-id')
    page_obj = paginated_queryset(request, rec, 10)
    
    filter_params = request.GET.copy()
    if 'page' in filter_params:
        del filter_params['page']
        
    teacher_redirect_url = request.get_full_path()
    request.session['teacher_redirect_url'] = teacher_redirect_url
    
    return render(request, 'teachers_list.html', {
        'form': form,
        'rec': page_obj,
        'filter_params': filter_params.urlencode(),
    })

def create_teacher(request):
    """Create a new teacher (AJAX-friendly)."""
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    return JsonResponse({'success': True, 'message': 'Teacher created successfully!'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=500)
        else:
            errors = {
                field: [str(error) for error in error_list]
                for field, error_list in form.errors.items()
            }
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def update_teacher(request, id):
    """Update an existing teacher."""
    teacher_redirect_url = request.session.get('teacher_redirect_url')
    teacher = get_object_or_404(Teacher, id=id)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully.')
            if teacher_redirect_url:
                return redirect(teacher_redirect_url)
    else:
        form = TeacherForm(instance=teacher)
    return render(request, 'update_teacher.html', {'form': form, 'teacher': teacher})

def delete_teacher(request, id):
    """Delete a teacher."""
    teacher = get_object_or_404(Teacher, id=id)
    teacher_redirect_url = request.session.get('teacher_redirect_url')
    if teacher:
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully.')
        if teacher_redirect_url:
            return redirect(teacher_redirect_url)
    return redirect('teacher_list')






def subject_list(request):
    return render(request, 'subject_list.html')

def class_list(request):
    return render(request, 'class_list.html')

def timetable_view(request):
    return render(request, 'timetable.html')

def adjustment_today(request):
    return render(request, 'adjustment.html')


 
def add_dummy_data(request):
    # 1. Subjects
    subject_names = ["Maths", "Science", "English", "History", "Geography"]
    subjects = []
    for name in subject_names:
        obj, created = Subject.objects.get_or_create(name=name)
        subjects.append(obj)

    # 2. Teachers
    teacher_data = [
        {"name": "Mr. Sharma", "email": "sharma@example.com"},
        {"name": "Ms. Gupta", "email": "gupta@example.com"},
        {"name": "Mr. Khan", "email": "khan@example.com"},
        {"name": "Ms. Patel", "email": "patel@example.com"},
        {"name": "Mr. Singh", "email": "singh@example.com"},
        {"name": "Ms. Verma", "email": "verma@example.com"},
        {"name": "Ms. Das", "email": "das@example.com"},
        {"name": "Mr. Mehta", "email": "mehta@example.com"},
        {"name": "Ms. Reddy", "email": "reddy@example.com"},
        {"name": "Mr. Joshi", "email": "joshi@example.com"},
        {"name": "Ms. Nair", "email": "nair@example.com"},
        {"name": "Mr. Roy", "email": "roy@example.com"},
        {"name": "Ms. Chawla", "email": "chawla@example.com"},
        {"name": "Mr. Sinha", "email": "sinha@example.com"},
        {"name": "Ms. Pillai", "email": "pillai@example.com"},
    ]
    teachers = []
    for t in teacher_data:
        obj, created = Teacher.objects.get_or_create(
            email=t["email"],
            defaults={
                "name": t["name"],
                "capable_upto_class": 10,
                "is_class_teacher": False,
            }
        )
        teachers.append(obj)

    # 3. ClassRooms
    classroom_data = [
        {"name": "5A", "grade": 5, "section": "A"},
        {"name": "6B", "grade": 6, "section": "B"},
        {"name": "5B", "grade": 5, "section": "B"},
        {"name": "6A", "grade": 6, "section": "A"},
        {"name": "7A", "grade": 7, "section": "A"},
        {"name": "7B", "grade": 7, "section": "B"},
        {"name": "8A", "grade": 8, "section": "A"},
        {"name": "8B", "grade": 8, "section": "B"},
        {"name": "9A", "grade": 9, "section": "A"},
        {"name": "9B", "grade": 9, "section": "B"},
        {"name": "10A", "grade": 10, "section": "A"},
        {"name": "10B", "grade": 10, "section": "B"},
        {"name": "4A", "grade": 4, "section": "A"},
        {"name": "4B", "grade": 4, "section": "B"},
        {"name": "3A", "grade": 3, "section": "A"},
        {"name": "3B", "grade": 3, "section": "B"},
    ]
    classrooms = []
    for room in classroom_data:
        obj, created = ClassRoom.objects.get_or_create(
            name=room["name"],
            defaults={
                "grade": room["grade"],
                "section": room["section"],
                "class_teacher": teachers[0]
            }
        )
        classrooms.append(obj)

    # 4. Teacher-Subject-Class Assignment
    for teacher in teachers:
        for subject in subjects[:3]:  # Assign 3 subjects per teacher
            for room in classrooms:
                TeacherSubjectClassAssignment.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    classroom=room,
                    defaults={"lectures_per_week": 4}
                )

    # 5. Daily Lecture Timings (6 lectures per day)
    for day, _ in DAYS_OF_WEEK:
        for i in range(1, 8):  # 7 lectures per day
            start = time(hour=8 + i, minute=0)
            end = time(hour=8 + i, minute=45)
            DailyLectureTiming.objects.get_or_create(
                day=day,
                lecture_number=i,
                defaults={
                    "start_time": start,
                    "end_time": end
                }
            )

    return redirect('/')  # Redirect after adding data


 