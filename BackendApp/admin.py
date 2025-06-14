from django.contrib import admin
from .models import (
    Subject, Teacher, ClassRoom, TeacherSubjectClassAssignment,
    DailyLectureTiming, BreakClassAssignment, LectureSchedule,
    TeacherLeave, ProxyAssignment, Institute
)

admin.site.register(Subject)
admin.site.register(Teacher)
admin.site.register(ClassRoom)
admin.site.register(TeacherSubjectClassAssignment)
admin.site.register(DailyLectureTiming)
admin.site.register(BreakClassAssignment)
admin.site.register(LectureSchedule)
admin.site.register(TeacherLeave)
admin.site.register(ProxyAssignment)
admin.site.register(Institute)
