from django.contrib import admin
from .models import (
    Subject,
    Teacher,
    ClassRoom,
    TeacherSubjectClassAssignment,
    DailyTimingSlots,
    DailyLectureTiming,
    BreakClassAssignment,
    LectureSchedule,
    TeacherLeave,
    ProxyAssignment,
    Institute,
)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone")
    search_fields = ("name", "email")
    filter_horizontal = ("capable_classes_for_proxy",)

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "grade", "section", "class_teacher")
    search_fields = ("name", "grade", "section")
    list_filter = ("grade",)

@admin.register(TeacherSubjectClassAssignment)
class TeacherSubjectClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher", "subject", "classroom", "lectures_per_week")
    search_fields = ("teacher__name", "subject__name", "classroom__name")
    list_filter = ("teacher", "subject", "classroom")

@admin.register(DailyTimingSlots)
class DailyTimingSlotsAdmin(admin.ModelAdmin):
    list_display = ("id", "day", "lecture_number", "start_time", "end_time")
    list_filter = ("day",)
    ordering = ("day", "lecture_number")

@admin.register(DailyLectureTiming)
class DailyLectureTimingAdmin(admin.ModelAdmin):
    list_display = ("id", "lecture_number", "lecture_name", "time_slot")
    list_filter = ("time_slot__day",)

@admin.register(BreakClassAssignment)
class BreakClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "lecture_timing", "break_type", "min_grade", "max_grade")
    filter_horizontal = ("classrooms",)
    list_filter = ("break_type",)

@admin.register(LectureSchedule)
class LectureScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "day", "lecture_timing", "classroom", "subject", "teacher")
    list_filter = ("day", "classroom", "teacher", "subject")
    search_fields = ("classroom__name", "subject__name", "teacher__name")
    ordering = ("day", "lecture_timing__lecture_number")

@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher", "date", "reason")
    list_filter = ("teacher", "date")
    search_fields = ("teacher__name", "reason")

@admin.register(ProxyAssignment)
class ProxyAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "lecture_timing", "absent_teacher", "proxy_teacher", "classroom", "subject")
    list_filter = ("date", "classroom", "absent_teacher", "proxy_teacher")
    search_fields = ("absent_teacher__name", "proxy_teacher__name", "classroom__name")

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_email", "address")
    search_fields = ("name", "contact_email")