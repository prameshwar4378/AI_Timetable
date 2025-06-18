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
        fields = ['name', 'email', 'phone',  'capable_classes_for_proxy']


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
        fields = ['time_slot', 'lecture_number']

 
class BreakClassAssignmentForm(forms.ModelForm):
    class Meta:
        model = BreakClassAssignment
        fields = ['lecture_timing', 'break_type', 'min_grade', 'max_grade']

    auto_assign = forms.BooleanField(
        required=False,
        help_text="Auto-select classrooms from min to max grade."
    )

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('auto_assign'):
            qs = ClassRoom.objects.all()
            if instance.min_grade is not None and instance.max_grade is not None:
                qs = qs.filter(grade__gte=instance.min_grade, grade__lte=instance.max_grade)
                if commit:
                    instance.save()
                    instance.classrooms.set(qs)
        if commit:
            instance.save()
        return instance



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
