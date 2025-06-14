from django import forms
from .models import (
    Subject, Teacher, ClassRoom, TeacherSubjectClassAssignment,
    DailyLectureTiming, BreakClassAssignment, LectureSchedule,
    TeacherLeave, ProxyAssignment, Institute
)

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'phone', 'is_class_teacher', 'capable_upto_class']


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['name', 'grade', 'section', 'class_teacher']


class TeacherSubjectClassAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectClassAssignment
        fields = ['teacher', 'subject', 'classroom', 'lectures_per_week']


class DailyLectureTimingForm(forms.ModelForm):
    class Meta:
        model = DailyLectureTiming
        fields = ['day', 'lecture_number', 'start_time', 'end_time']


class BreakClassAssignmentForm(forms.ModelForm):
    class Meta:
        model = BreakClassAssignment
        fields = ['lecture_timing', 'classroom']


class LectureScheduleForm(forms.ModelForm):
    class Meta:
        model = LectureSchedule
        fields = ['date', 'day', 'lecture_timing', 'classroom', 'subject', 'teacher']


class TeacherLeaveForm(forms.ModelForm):
    class Meta:
        model = TeacherLeave
        fields = ['teacher', 'date', 'reason']


class ProxyAssignmentForm(forms.ModelForm):
    class Meta:
        model = ProxyAssignment
        fields = ['date', 'lecture_timing', 'absent_teacher', 'proxy_teacher', 'classroom', 'subject']


class InstituteForm(forms.ModelForm):
    class Meta:
        model = Institute
        fields = ['name', 'address', 'contact_email', 'logo']
