from django.shortcuts import render,redirect
from .models import *
from django.utils import timezone
from datetime import time



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .utils import paginated_queryset



def dashboard(request):
    return render(request, 'dashboard.html')



def teacher_list(request): 
    return render(request, 'teachers_list.html',   )

def create_teacher(request): 
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def update_teacher(request, id): 
    return render(request, 'update_teacher.html' )

def delete_teacher(request, id): 
    return redirect('teacher_list')

def subject_list(request):
    return render(request, 'subject_list.html')

def class_list(request):
    return render(request, 'class_list.html')

def timetable_view(request):
    return render(request, 'timetable.html')

def adjustment_today(request):
    return render(request, 'adjustment.html')

from django.shortcuts import render, redirect
from .forms import BreakClassAssignmentForm

def break_assignment(request):
    data= BreakClassAssignment.objects.all() 
    for i in data:
        print(f'the {i.classrooms}' 'are assigned to {i.subject}')
    if request.method == "POST":
        form = BreakClassAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/software/break_assignment/')  # Replace with your success URL
    else:
        form = BreakClassAssignmentForm()

    return render(request, 'assign_break.html', {'form': form, 'data': data})


def add_dummy_data(request):
    # 1. Subjects
    subject_names = ["Maths", "Science", "English", "History", "Geography", "Computer", "Hindi", "Sanskrit"]
    subjects = [Subject.objects.get_or_create(name=name)[0] for name in subject_names]

    # 2. Teachers
    teachers = []
    for i in range(1, 21):
        teacher, _ = Teacher.objects.get_or_create(
            email=f"teacher{i}@school.com",
            defaults={
                "name": f"Teacher {i}",
                "phone": f"99999999{i:02d}",
            }
        )
        teachers.append(teacher)

    # 3. ClassRooms
    classrooms = []
    for grade in range(1, 11):  # Class 1 to 10
        for sec in ['A', 'B']:
            room_name = f"{grade}{sec}"
            class_teacher = teachers[(grade * ord(sec)) % len(teachers)]
            classroom, _ = ClassRoom.objects.get_or_create(
                name=room_name,
                defaults={
                    "grade": grade,
                    "section": sec,
                    "class_teacher": class_teacher
                }
            )
            classrooms.append(classroom)

    # 4. Set capable_classes_for_proxy
    for teacher in teachers:
        teacher.capable_classes_for_proxy.set(classrooms[:10])  # Assign first 10 classes
        teacher.save()

    # 5. TeacherSubjectClassAssignment
    for teacher in teachers:
        for subject in subjects[:3]:
            for classroom in classrooms[:3]:  # Assign only a few to avoid too much data
                TeacherSubjectClassAssignment.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    classroom=classroom,
                    defaults={"lectures_per_week": 4}
                )

    # 6. DailyTimingSlots & DailyLectureTiming
    lecture_labels = {
        1: ("1", "1st Period"),
        2: ("2", "2nd Period"),
        3: ("3", "3rd Period"),
        4: ("4", "Lunch Break"),
        5: ("5", "4th Period"),
        6: ("6", "5th Period"),
        7: ("S", "Short Recess"),
    }

    for day_key, _ in DAYS_OF_WEEK:
        for i in range(1, 8):
            lecture_number, lecture_name = lecture_labels[i]
            start = time(hour=7 + i, minute=0)
            end = time(hour=7 + i, minute=45)

            timing_slot, _ = DailyTimingSlots.objects.get_or_create(
                day=day_key,
                lecture_number=i,
                defaults={"start_time": start, "end_time": end}
            )

            DailyLectureTiming.objects.get_or_create(
                lecture_number=lecture_number,
                lecture_name=lecture_name,
                time_slot=timing_slot
            )

    # 7. Assign Breaks by Grade Group
    # Get lecture timings for lunch break slots
    for day_key, _ in DAYS_OF_WEEK:
        lunch_3rd = DailyLectureTiming.objects.filter(
            lecture_number="3",
            lecture_name="Lunch Break",
            time_slot__day=day_key
        ).first()

        lunch_4th = DailyLectureTiming.objects.filter(
            lecture_number="4",
            lecture_name="Lunch Break",
            time_slot__day=day_key
        ).first()

        # Group 1: Classes 1 to 5 → Lunch at 3rd slot
        break1, _ = BreakClassAssignment.objects.get_or_create(lecture_timing=lunch_3rd)
        class_1_to_5 = ClassRoom.objects.filter(grade__gte=1, grade__lte=5)
        break1.classroom.set(class_1_to_5)
        break1.save()

        # Group 2: Classes 6 to 10 → Lunch at 4th slot
        break2, _ = BreakClassAssignment.objects.get_or_create(lecture_timing=lunch_4th)
        class_6_to_10 = ClassRoom.objects.filter(grade__gte=6, grade__lte=10)
        break2.classroom.set(class_6_to_10)
        break2.save()

    return redirect('/')
