from django.core.management.base import BaseCommand
from timetable_confugration import extract_timetable_data
from timetable_confugration import generate_school_timetable
from .models import DailyLectureTiming, ClassRoom, Subject, Teacher, LectureSchedule

class Command(BaseCommand):
    help = "Automatically generate the school timetable using OR-Tools"

    def handle(self, *args, **options):
        data = extract_timetable_data()
        timetable = generate_school_timetable(**data)

        if not timetable:
            self.stdout.write(self.style.ERROR("No feasible timetable found!"))
            return

        # Optionally, clear existing timetable
        LectureSchedule.objects.all().delete()

        # Save results to LectureSchedule
        for entry in timetable:
            classroom = ClassRoom.objects.get(id=entry['class_id'])
            timing = DailyLectureTiming.objects.get(id=entry['slot_idx'])
            subject = Subject.objects.get(id=entry['subject_id'])
            teacher = Teacher.objects.get(id=entry['teacher_id'])
            LectureSchedule.objects.create(
                date=None,  # Set if you want per-date, or leave null for generic week
                day=timing.time_slot.day,
                lecture_timing=timing,
                classroom=classroom,
                subject=subject,
                teacher=teacher,
            )
        self.stdout.write(self.style.SUCCESS("Timetable generated and saved!"))