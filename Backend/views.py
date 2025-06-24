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





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
from Backend.models import (
    Teacher, ClassRoom, Subject, TeacherSubjectClassAssignment,
    DailyLectureTiming, LectureSchedule
)
# from services.or_tools_timetable import generate_school_timetable

def fake_generate_school_timetable(**kwargs):

    print("Status: OR-Tools timetable generation started...")
    print("Status: Received data keys:", list(kwargs.keys()))
    # Simulate processing
    print("Status: Processing data...")
    # Simulate result
    print("Status: Timetable generation complete (FAKE DATA)!")
    # Return fake timetable for test
    return [
        {
            "class_id": kwargs['classes'][0] if kwargs['classes'] else 1,
            "day": "Monday",
            "slot_idx": kwargs['lecture_slots'].get("Monday", [1])[0],
            "subject_id": kwargs['subjects'][0] if kwargs['subjects'] else 1,
            "teacher_id": kwargs['teachers'][0] if kwargs['teachers'] else 1,
        }
    ]

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .timetable_confugration import extract_timetable_data, generate_school_timetable, preanalyze_assignments,auto_adjust_teacher_lectures
from .models import DailyLectureTiming, ClassRoom, Subject, Teacher, LectureSchedule
from django.http import JsonResponse 
# Import your functions/models as needed
# from .models import LectureSchedule, ClassRoom, DailyLectureTiming, Subject, Teacher

@csrf_exempt
def generate_timetable_view(request):
    print("🔔 Timetable generation triggered.")
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=405)

    # FIRST: extract data from your source
    data = extract_timetable_data()  # <-- This line must come BEFORE pre-analysis

    # NOW: run pre-analysis
    ok = preanalyze_assignments(data["teacher_subject_class_assignment"], data["lecture_slots"])
    if not ok:
        return JsonResponse({
            "success": False,
            "error": "Conflicts detected in assignments. Check the server logs for details."
        }, status=400)

    timetable = generate_school_timetable(**data)
    # ====== SAVE THE GENERATED TIMETABLE ======
    for entry in timetable:
        try:
            print("@@@@@@@@@ SAVING:", entry)
            classroom = ClassRoom.objects.get(id=entry['class_id'])
            timing = DailyLectureTiming.objects.get(id=entry['slot_idx'])
            subject = Subject.objects.get(id=entry['subject_id'])
            teacher = Teacher.objects.get(id=entry['teacher_id'])
            obj = LectureSchedule.objects.create(
                day=timing.time_slot.day,
                lecture_timing=timing,
                classroom=classroom,
                subject=subject,
                teacher=teacher,
            )
            print("SAVED:", obj)
        except Exception as e:
            print("ERROR SAVING ENTRY:", entry, "ERROR:", e)
    # ====== END SAVE BLOCK ======

    return JsonResponse({"success": True, "message": "Timetable generated and saved! (empty slots left for manual fill)"})

# def generate_timetable_view(request):
#     # if request.method != "POST":
#     #     print("Status: Received non-POST request")
#     #     return JsonResponse({"error": "POST request required."}, status=405)

#     print("Status: Extracting teachers, classes, and subjects...")
#     teachers = list(Teacher.objects.values_list('id', flat=True))
#     classes = list(ClassRoom.objects.values_list('id', flat=True))
#     subjects = list(Subject.objects.values_list('id', flat=True))

#     print("Status: Mapping class teachers...")
#     class_teacher_map = {}
#     for classroom in ClassRoom.objects.select_related('class_teacher'):
#         if classroom.class_teacher:
#             class_teacher_map[classroom.id] = classroom.class_teacher.id

#     print("Status: Collecting teacher-subject-class assignments...")
#     teacher_subject_class_assignment = {}
#     subject_lecture_weekly_count = defaultdict(int)
#     for assign in TeacherSubjectClassAssignment.objects.all():
#         key = (assign.teacher.id, assign.subject.id, assign.classroom.id)
#         teacher_subject_class_assignment[key] = assign.lectures_per_week
#         subject_lecture_weekly_count[(assign.classroom.id, assign.subject.id)] += assign.lectures_per_week

#     print("Status: Collecting lecture slots per day...")
#     lecture_slots = defaultdict(list)
#     slot_idx_map = {}
#     for timing in DailyLectureTiming.objects.select_related('time_slot'):
#         day = timing.time_slot.day
#         slot = timing.time_slot.lecture_number
#         slot_idx_map[(day, slot)] = timing.id
#         lecture_slots[day].append(timing.id)

#     print("Status: Collecting teacher max lectures/week...")
#     MAX_LECTURES = 30
#     teacher_max_lectures = {t.id: MAX_LECTURES for t in Teacher.objects.all()}

#     print("Status: Collecting teacher availability (all available for test)...")
#     teacher_availability = defaultdict(lambda: True)

#     print("Status: Collecting Saturday lecture slots...")
#     saturday_lecture_slots = [
#         timing.id
#         for timing in DailyLectureTiming.objects.select_related('time_slot').filter(time_slot__day='Saturday')
#     ]

#     print("Status: Preparing data for timetable generation...")
#     data = dict(
#         teachers=teachers,
#         classes=classes,
#         subjects=subjects,
#         class_teacher_map=class_teacher_map,
#         teacher_subject_class_assignment=teacher_subject_class_assignment,
#         lecture_slots=lecture_slots,
#         subject_lecture_weekly_count=subject_lecture_weekly_count,
#         teacher_max_lectures=teacher_max_lectures,
#         teacher_availability=teacher_availability,
#         breaks={},
#         saturday_lecture_slots=saturday_lecture_slots,
#     )

#     print("Status: Calling timetable generator...")
#     # timetable = generate_school_timetable(**data)
#     timetable = fake_generate_school_timetable(**data)

#     if not timetable:
#         print("Status: Timetable generation failed!")
#         return JsonResponse({"success": False, "error": "No feasible timetable found!"}, status=400)

#     print("Status: Clearing previous timetable...")
#     LectureSchedule.objects.all().delete()

#     print("Status: Saving new timetable...")
#     for entry in timetable:
#         try:
#             classroom = ClassRoom.objects.get(id=entry['class_id'])
#             timing = DailyLectureTiming.objects.get(id=entry['slot_idx'])
#             subject = Subject.objects.get(id=entry['subject_id'])
#             teacher = Teacher.objects.get(id=entry['teacher_id'])
#             LectureSchedule.objects.create(
#                 day=timing.time_slot.day,
#                 lecture_timing=timing,
#                 classroom=classroom,
#                 subject=subject,
#                 teacher=teacher,
#             )
#             print("Record created:", classroom, timing, subject, teacher)
#         except Exception as e:
#             print("Error creating record:", e)

#     print("Status: Timetable generation and saving complete!")
#     return JsonResponse({"success": True, "message": "Timetable (FAKE DATA) generated and saved!"})



