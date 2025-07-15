"""school_advance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from school.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from school.views import ResetPasswordView


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', home_page,name='home_page'),
    path('contactus', contactus,name='contactus'),
    path('view_contactus', view_contactus,name='view_contactus'),
    path('replay_contactus/<id>', replay_contactus,name='replay_contactus'),
   
    path('admin_view_student/<id>', admin_view_student,name='admin_view_student'),
    path('admin_view_parent/<id>', admin_view_parent,name='admin_view_parent'),
    path('student/', add,name='add'),
    path('add_student/', add_student,name='add_student'),
    path('update_student/<id>', update_student,name='update_student'),
    path('delete_student/<id>', delete_student,name='delete_student'),
    
    path('add_subject/', add_subject,name='add_subject'),
    path('update_subject/<id>', update_subject,name='update_subject'),
    path('delete_subject/<id>', delete_subject,name='delete_subject'),

    path('add_gallery/', add_gallery,name='add_gallery'),
    path('view_gallery/', view_gallery,name='view_gallery'),
    path('update_gallery/<id>', update_gallery,name='update_gallery'),
    path('delete_gallery/<id>', delete_gallery,name='delete_gallery'),

    path('add-activity/', add_activity,name='add_activity'),
    path('activity/', activity,name='activity'),
    path('delete_activity/<id>', delete_activity,name='delete_activity'),
    path('update_activity/<id>', update_activity,name='update_activity'),

    path('progress_chart/', progress_chart,name='progress_chart'),
    
    path('gallery/', gallery,name='gallery'),
    path('aboutus/', aboutus,name='aboutus'),
    path('login_page/', login_page,name='login_page'),
    path('logout_page/', logout_page,name='logout_page'),
    path('change_password/', change_password,name='change_password'),

    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
     path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),


    path('superuser_details/', superuser_details,name='superuser_details'),
    path('admin_dash/', admin_dash,name='admin_dash'),
    path('teacher_dash/', teacher_dash,name='teacher_dash'),
    path('parent_dash/', parent_dash,name='parent_dash'),
    path('create_user/', create_user,name='create_user'),
    path('delete_user/<id>', delete_user,name='delete_user'),
    path('add_parent/', add_parent,name='add_parent'),
    path('add_teacher/', add_teacher,name='add_teacher'),
    path('view_teacher/<id>', view_teacher,name='view_teacher'),
    path('view_parent_teacher/', view_parent_teacher,name='view_parent_teacher'),

    path('teacher_add_marks/', teacher_add_marks,name='teacher_add_marks'),
    path('add_marks/<id>', add_marks,name='add_marks'),
    path('update_marks/<id>', update_marks,name='update_marks'),
    path('delete_marks/<id>', delete_marks,name='delete_marks'),

    path('add_curriculum/', add_curriculum,name='add_curriculum'),
    path('update_curriculum/<id>', update_curriculum,name='update_curriculum'),
    path('delete_curriculum/<id>', delete_curriculum,name='delete_curriculum'),

    path('add_ptm/', add_ptm,name='add_ptm'),
    path('update_ptm/<id>', update_ptm,name='update_ptm'),
    path('delete_ptm/<id>', delete_ptm,name='delete_ptm'),

    path('add_timetable/', add_timetable,name='add_timetable'),
    path('view_timetable/', view_timetable,name='view_timetable'),
    path('delete_timetable/<id>', delete_timetable,name='delete_timetable'),
    path('update_timetable/<id>', update_timetable,name='update_timetable'),

    path('attendance/', attendance,name='attendance'),
    path('add_attedance/<id>', add_attedance,name='add_attedance'),
    path('update_attendance/<id>', update_attendance,name='update_attendance'),
    path('delete_attedance/<id>', delete_attedance,name='delete_attedance'),


    path('teacher_view_details/', teacher_view_details,name='teacher_view_details'),
    path('teacher_update_details/<id>', teacher_update_details,name='teacher_update_details'),

    path('parent_add_details/', parent_add_details,name='parent_add_details'),
    path('quiz/', quiz,name='quiz'),
    path('parent_update_details/<id>', parent_update_details,name='parent_update_details'),
    path('parent_view_student/', parent_view_student,name='parent_view_student'),
    path('parent_view_marks/', parent_view_marks,name='parent_view_marks'),
    path('parent_view_attendance/', parent_view_attendance,name='parent_view_attendance'),
    path('parent_view_timetable/', parent_view_timetable,name='parent_view_timetable'),
    path('parent_view_ptm/', parent_view_ptm,name='parent_view_ptm'),
    path('parent_view_curriculum/', parent_view_curriculum,name='parent_view_curriculum'),
    
    path('generate_fee_report_pdf/', generate_fee_report_pdf,name='generate_fee_report_pdf'),

    path('class_teacher/', class_teacher,name='class_teacher'), 
    path('update_class_teacher/<id>', update_class_teacher,name='update_class_teacher'), 
    path('delete_class_teacher/<id>', delete_class_teacher,name='delete_class_teacher'),

    path('change_password_s', change_password_s,name='change_password_s'),

    path('reports/', generate_attendance_report_pdf,name='generate_attendance_report_pdf'),
    path('generate_marks_report_pdf/', generate_marks_report_pdf,name='generate_marks_report_pdf'),
]
 
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns+=staticfiles_urlpatterns()