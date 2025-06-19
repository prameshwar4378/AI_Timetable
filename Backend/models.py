from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

# ------------------------------
# 1. Subject & Class Structure
# ------------------------------

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    capable_classes_for_proxy = models.ManyToManyField('ClassRoom', blank=True)

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=50)  # e.g. "Nursery", "5A"
    grade = models.PositiveIntegerField(help_text="Use 0 for Nursery/LKG/UKG")
    section = models.CharField(max_length=5, blank=True, null=True)
    class_teacher = models.ForeignKey(Teacher, null=True, blank=True, on_delete=models.SET_NULL, related_name="class_teacher_of")

    def __str__(self):
        return f"{self.name}"


class TeacherSubjectClassAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    lectures_per_week = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('teacher', 'subject', 'classroom')

    def __str__(self):
        return f"{self.teacher} → {self.subject} ({self.classroom})"

# ------------------------------
# 2. Lecture Timing Setup
# ------------------------------

DAYS_OF_WEEK = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
]

class DailyTimingSlots(models.Model):
    day = models.CharField(choices=DAYS_OF_WEEK, max_length=10)
    lecture_number = models.PositiveIntegerField(help_text="Lecture slot number (e.g., 1st period = 1)")
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('day', 'lecture_number')
        ordering = ['day', 'lecture_number']

    def __str__(self):
        return f"{self.day} - Lecture {self.lecture_number} ({self.start_time} to {self.end_time})"

class DailyLectureTiming(models.Model):
    lecture_number = models.CharField(max_length=5)  # e.g. "1", "2", "3", "L"
    lecture_name = models.CharField(max_length=50)   # e.g. "1st Period", "Lunch Break"
    time_slot = models.ForeignKey(DailyTimingSlots, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.time_slot.day} - {self.lecture_name} ({self.time_slot.start_time} to {self.time_slot.end_time})"



class BreakClassAssignment(models.Model):
    lecture_timing = models.ForeignKey(DailyLectureTiming, on_delete=models.CASCADE)
    classrooms = models.ManyToManyField(ClassRoom)
    # New fields for dynamic config
    break_type = models.CharField(max_length=50, default="Lunch Break")  # e.g. Lunch Break, Short Recess
    min_grade = models.PositiveIntegerField(null=True, blank=True)
    max_grade = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.break_type} during {self.lecture_timing} for Grades {self.min_grade}-{self.max_grade}"



# ------------------------------
# 3. Timetable & Lecture Slots
# ------------------------------

class LectureSchedule(models.Model):
    date = models.DateField()
    day = models.CharField(choices=DAYS_OF_WEEK, max_length=10)
    lecture_timing = models.ForeignKey(DailyLectureTiming, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('date', 'lecture_timing', 'classroom')
        ordering = ['date', 'lecture_timing__lecture_number']

    def __str__(self):
        return f"{self.date} {self.classroom} - {self.subject} ({self.teacher})"

# ------------------------------
# 4. Leave & Proxy Management
# ------------------------------

class TeacherLeave(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField(blank=True)

    class Meta:
        unique_together = ('teacher', 'date')

    def __str__(self):
        return f"{self.teacher.name} on leave ({self.date})"


class ProxyAssignment(models.Model):
    date = models.DateField()
    lecture_timing = models.ForeignKey(DailyLectureTiming, on_delete=models.CASCADE)
    absent_teacher = models.ForeignKey(Teacher, related_name="absent_teacher", on_delete=models.CASCADE)
    proxy_teacher = models.ForeignKey(Teacher, related_name="proxy_teacher", on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('date', 'lecture_timing', 'classroom')

    def __str__(self):
        return f"Proxy: {self.proxy_teacher} for {self.absent_teacher} ({self.date}, {self.classroom})"

# ------------------------------
# 5. Optional: Institute Setup (Optional Extension)
# ------------------------------

class Institute(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_email = models.EmailField()
    logo = models.ImageField(upload_to="institute_logos/", blank=True, null=True)
    log1 = models.ImageField(upload_to="institute_logos/", blank=True, null=True)

    def __str__(self):
        return self.name
