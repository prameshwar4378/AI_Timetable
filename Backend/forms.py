from django import forms
from .models import *

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
    repeat_weekdays = forms.BooleanField(
        required=False,
        help_text="Repeat this break Monday to Friday (same slot, same classrooms)"
    )

    class Meta:
        model = BreakClassAssignment
        fields = ['lecture_timing', 'classrooms', 'break_type']

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()
            self.save_m2m()

        if self.cleaned_data.get('repeat_weekdays'):
            original_slot = instance.lecture_timing.time_slot
            # Fetch all time slots on same lecture_number but different days
            repeat_slots = DailyTimingSlots.objects.filter(
                lecture_number=original_slot.lecture_number
            ).exclude(day=original_slot.day)

            for slot in repeat_slots:
                try:
                    timing = DailyLectureTiming.objects.get(time_slot=slot)
                    new_break = BreakClassAssignment.objects.create(
                        lecture_timing=timing,
                        break_type=instance.break_type
                    )
                    new_break.classrooms.set(instance.classrooms.all())
                except DailyLectureTiming.DoesNotExist:
                    continue

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
