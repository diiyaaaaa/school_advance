from django.shortcuts import render,redirect, get_object_or_404
from school.models import *
from django.db.models import Sum
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
import datetime
from collections import defaultdict
import numpy as np
from django.db.models import Count
from .forms import *
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime,timedelta
import os
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.http import HttpResponse


# Create your views here.

def home_page(request):
    return render(request,'home.html')
   

def login_page(request):
    if request.method == "POST":
        un=request.POST.get("uname")
        password=request.POST.get("password")

        if not User.objects.filter(username=un).exists:
          err="with this username no user is exsist"
          data={
                'err':err
            }
          return render(request,'login.html',data)

        user=authenticate(username=un,password=password)
            
        if user is None:
            error="Invalid password"
            data={
                'error':error
            }
            return render(request,'login_page.html',data)
        else:
            login(request,user)
            if Group.objects.filter(user=user,name='teacher').exists():
                return redirect('teacher_dash')
            elif Group.objects.filter(user=user,name='parent').exists():
                return redirect('parent_dash')
            return redirect('/admin_dash/')
    return render(request,'login_page.html')


def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']
        user = request.user
        if user.check_password(old_password) and new_password1 == new_password2:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)  # Important to maintain session
            messages.success(request,"Password changed successfully! ")
            return redirect('login_page')
    return render(request, 'change_password.html')


from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('login_page')



def is_superuser(user):
    return user.is_superuser

def is_teacher(user):
    return user.groups.filter(name='teacher').exists()

def is_parent(user):
    return user.groups.filter(name='parent').exists()

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def superuser_details(request):
    if request.user.is_superuser:
        superuser = request.user
    return render(request, 'superuser_details.html', {'superuser': superuser})

@login_required(login_url='/login_page/')
@user_passes_test(is_teacher)
def teacher_dash(request):
    user = Teacher_user.objects.get(teacher_user=request.user)  
    teacher=Teacher.objects.get(t_user=user)
    salary=teacher.salary
    total_student=Student.objects.all().count() 
    total_teacher=Teacher.objects.all().count() 
    data={'salary':salary,'total_student':total_student,'total_teacher':total_teacher}
    return render(request,'teacher_dash.html',data)

@login_required(login_url='/login_page/')
@user_passes_test(is_parent)
def parent_dash(request):
    return render(request,'parent_sidebar.html')

def logout_page(request):
    logout(request)
    return redirect('login_page')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_student(request):
    cls = Class.objects.all()
    parent = Parent.objects.all()
    if request.method == 'POST':
        data = request.POST
        fn = data.get('fname')
        ln = data.get('lname')
        rollno = data.get('rollno')
        gender = data.get('gender')
        img = request.FILES.get('img')
        e_date = data.get('e_date')
        dob = data.get('stu_dob')
        address = data.get('address')
        medium = request.POST.get('medium')
        cls_id = request.POST.get('class')
        cls_name = Class.objects.get(id=cls_id)
        p_id = request.POST.get('parent')
        parent = Parent.objects.get(id=p_id)
        fees = data.get('fees')
        status = data.get('status')
        phone = data.get('phone')
        a_year = data.get('a_year')

        # Validate roll number
        if not rollno.isdigit() or int(rollno) <= 0:
            messages.error(request, "Roll number must be a positive integer greater than zero.")
            return redirect('add_student')

        existing_student = Student.objects.filter(roll_no=rollno, cls_name=cls_id, medium_name=medium)
        if existing_student.exists():
            messages.error(request, "A student with the same roll number already exists in this class.")
            return redirect('add_student')

        # Validate first name and last name
        if len(fn.strip()) < 2 or len(ln.strip()) < 2:
            messages.error(request, "First name and last name must be at least 2 characters long.")
            return redirect('add_student')

        # Validate phone number
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must consist of exactly 10 digits.")
            return redirect('add_student')

        # Validate image upload
        if img:
            if not img.content_type.startswith('image'):
                messages.error(request, 'Please upload a valid image file.')
                return redirect('add_student')
        else:
            messages.error(request, 'Please upload an image file.')
            return redirect('add_student')

        # Save student data
        x = Student(
            dob=dob, fname=fn, lname=ln, roll_no=rollno, enroll_date=e_date, gender=gender, phone_no=phone,
            fee=fees, fee_status=status, acd_year=a_year, address=address, cls_name=cls_name, medium_name=medium,
            stu_img=img, parent=parent
        )
        x.save()
        messages.success(request,"Student added successfully")
        return redirect('add')
    return render(request,'add_student.html',{'cls':cls,'parent':parent})


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def update_student(request, id):
    qry = Student.objects.get(id=id)
    s_rollno = qry.roll_no

    cls = Class.objects.all()
    parent = Parent.objects.all()
    if request.method == 'POST':
        data = request.POST
        fn = data.get('fname')
        ln = data.get('lname')
        rollno = data.get('rollno')
        gender = data.get('gender')
        img = request.FILES.get('img')
        e_date = data.get('e_date')
        dob = data.get('dob')
        address = data.get('address')
        medium = data.get('medium')
        cls_id = data.get('class')
        cls_name = Class.objects.get(id=cls_id)
        p_id = data.get('parent')
        parent = Parent.objects.get(id=p_id)
        fees = data.get('fees')
        status = data.get('status')
        phone = data.get('phone')
        a_year = data.get('a_year')

        # Validate first name and last name
        if len(fn.strip()) < 2 or len(ln.strip()) < 2:
            messages.error(request, "First name and last name must be at least 2 characters long.")
            return redirect('update_student', id=id)

        # Validate phone number
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must consist of exactly 10 digits.")
            return redirect('update_student', id=id)

        # Validate roll number
        if not rollno.isdigit() or int(rollno) <= 0:
            messages.error(request, "Roll number must be a positive integer greater than zero.")
            return redirect('update_student', id=id)

        existing_student = Student.objects.exclude(roll_no=s_rollno).filter(roll_no=rollno, cls_name=cls_id)
        if existing_student.exists():
            messages.error(request, "A student with the same roll number already exists in this class.")
            return redirect('update_student', id=id)

        # Validate image upload
        if img:
            if not img.content_type.startswith('image'):
                messages.error(request, 'Please upload a valid image file.')
                return redirect('update_student', id=id)
        else:
             messages.error(request, 'Please upload an image file.')
             return redirect('update_student', id=id)

        # Save student data
        qry.acd_year = a_year
        qry.fname = fn
        qry.lname = ln
        qry.roll_no = rollno
        qry.enroll_date = e_date
        qry.dob = dob
        qry.cls_name = cls_name
        qry.medium_name = medium
        qry.parent = parent
        qry.fee = fees
        qry.fee_status = status
        qry.phone_no = phone
        qry.gender = gender
        qry.address = address

        if img:
            qry.stu_img = img

        qry.save()
        messages.success(request,"Student updated successfully")

        return redirect('add')

    return render(request,'update_student.html',{'qry':qry,'cls':cls,'parent':parent})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_student(request,id):
    qry=Student.objects.get(id=id)
    qry.delete()
    return redirect('add')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def admin_view_parent(request,id):
    parent=Parent.objects.get(id=id)
    stu=Student.objects.filter(parent=id)
    
    data={'parent':parent,'stu':stu}
    return render(request,'admin_view_parent.html',data)

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def admin_view_student(request,id): 
    s_id=Student.objects.get(id=id) 
    students=Student.objects.filter(id=id) 
    attendance=Attendance.objects.filter(stu_rollno=s_id) 
    marks=Marks.objects.filter(student=s_id)
    parent=s_id.parent
    semester_1_marks = Marks.objects.filter(student__in=students, exam='Semester-1')
    semester_2_marks = Marks.objects.filter(student__in=students, exam='Semester-2')
    data= {'attendance':attendance,'marks':marks,'students':students,'semester_1_marks':semester_1_marks,'semester_2_marks':semester_2_marks,'parent':parent} 
    return render(request,'admin_view_student.html',data)    

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_gallery(request):
    qry=Gallery.objects.all()
    if request.method=='POST':
        data=request.POST

        img_name=data.get('img_name')
        img=request.FILES.get('img')
        img_desc=data.get('img_desc')

        if img:
            
            if img.content_type.startswith('image'):
                pass
            else:
                messages.error(request, "Only image files are allowed.")
                return redirect('add_gallery')

        x=Gallery(img=img,img_desc=img_desc)
        x.save()

        messages.error(request, "Added Successfully!")
        return redirect('add_gallery')
    return render(request,'add_gallery.html',{'qry':qry})

def view_gallery(request):
    qry=Gallery.objects.all()
    return render(request,'view_gallery.html',{'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_gallery(request,id):
    qry=Gallery.objects.get(id=id)
    qry.delete()
    return redirect('add_gallery')


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def update_gallery(request, id):
    try:
        qry = Gallery.objects.get(id=id)
    except Gallery.DoesNotExist:
        messages.error(request, "Gallery does not exist.")
        return redirect('add_gallery')

    if request.method == 'POST':
        img_name = request.POST.get('img_name')
        img_desc = request.POST.get('img_desc')
        img = request.FILES.get('img')

        if img:
            if not img.content_type.startswith('image'):
                messages.error(request, "Only image files are allowed.")
                return redirect('add_gallery')

            qry.img = img

        qry.img_name = img_name
        qry.img_desc = img_desc
        qry.save()

        messages.success(request, "Gallery updated successfully!")
        return redirect('add_gallery')

    return render(request, 'update_gallery.html', {'qry': qry})

# def update_gallery(request,id):
#     qry=Gallery.objects.get(id=id)

#     if request.method=='POST':
#         img_name=request.POST.get('img_name')
#         img=request.FILES.get('img')
#         img_desc=request.POST.get('img_desc')

#         # if img:
#         #     if not img.content_type.startswith('image'):
#         #         messages.error(request, "Only image files are allowed.")
#         #         return redirect('add_gallery')

#         #     qry.img = img

#         qry.img_name=img_name
#         qry.img_desc=img_desc
#         qry.img = img
#         qry.save()
#         messages.error(request, "Updated Successfully!")
#         return redirect('add_gallery')
#     return render(request,'update_gallery.html',{'qry':qry})


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_activity(request):
    if request.method == 'POST':
        data = request.POST
        img_name = data.get('act_name')
        img = request.FILES.get('act_img')
        img_desc = data.get('act_desc')
        mon = data.get('mon')

        # Check if activity name already exists
        if Activity.objects.filter(act_name=img_name).exists():
            messages.error(request, "An activity with the same name already exists.")
            return redirect('add_activity')

        # Validate image upload
        if img:
            if not img.content_type.startswith('image'):
                messages.error(request, "Only image files are allowed.")
                return redirect('add_activity')

        # Save activity data
        x = Activity(act_img=img, act_desc=img_desc, act_name=img_name, date=mon)
        messages.error(request, "An activity added successfully!")
        x.save()

        return redirect('add_activity')
    
    qry=Activity.objects.all()
    data={'qry':qry}
    return render(request,'add_activity.html',data)

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_activity(request,id):
    qry=Activity.objects.get(id=id)
    qry.delete()
    return redirect('add_activity')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def update_activity(request,id):
    qry=Activity.objects.get(id=id)

    if request.method=='POST':
        data=request.POST

        img_name=data.get('act_name')
        img=request.FILES.get('act_img')
        img_desc=data.get('act_desc')
        mon = data.get('mon')

        if img:
            
            if img.content_type.startswith('image'):
                qry.act_img=img
                pass
            else:
                messages.error(request, "Only image files are allowed.")
                return redirect('add_activity')

        qry.act_name=img_name
        qry.act_desc=img_desc
        qry.date=mon
        
        qry.save()
        messages.error(request, "An activity updated successfully!")
        return redirect('add_activity')
    return render(request,'update_activity.html',{'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add(request):
    
    cls=Class.objects.all()
    data={}
    if request.method=="POST":
       
        medium=request.POST.get('medium')
        cls_id=request.POST.get('class')
        cls_name=Class.objects.get(id=cls_id)
        
        qry=Student.objects.filter(medium_name=medium,cls_name=cls_name)
        s_count=Student.objects.filter(medium_name=medium,cls_name=cls_name).count()
        
        paginator = Paginator(qry, 8)  
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        return render(request,'add.html',{'cls':cls, 'qry':page_obj,'s_count':s_count}) 
    students=Student.objects.all()
    return render(request,'add.html',{'cls':cls,'students':students})

def gallery(request):
    qry=Gallery.objects.all()
    return render(request,'gallery.html',{'qry':qry})

def activity(request):
    qry=Activity.objects.all()
    return render(request,'activity.html',{'qry':qry})

def aboutus(req):
    return render(req,'aboutus.html')


@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def attendance(request):
    cls=Class.objects.all()
    
    if request.method=="POST":
       
        medium=request.POST.get('medium')
        cls_id=request.POST.get('class')
        cls_name=Class.objects.get(id=cls_id)
        qry=Student.objects.filter(medium_name=medium,cls_name=cls_name)

        return render(request,'attendance.html',{'cls':cls, 'qry':qry})
    students=Student.objects.all()
    return render(request,'attendance.html',{'cls':cls,'students':students})

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def add_attedance(request,id):
    qry=Student.objects.get(id=id)

    if request.method=='POST':
        data=request.POST
        status=data.get('attd')
        rollno=data.get('rollno')
        date=data.get('date')
        if Attendance.objects.filter(stu_rollno=qry, date_of_attd=date).exists():
            messages.error(request, f"Attendance of Student for {date} already exists!")
            return redirect('attendance')

        # input_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Get today's date
        today_date = datetime.datetime.now().date()

        # Validate the date
        # if input_date > today_date:
        #     messages.error(request,"Selected date cannot be greater than today's date!")


        Attendance.objects.create(stu_rollno=qry,status=status,date_of_attd=date)
      
        messages.error(request, "Attendance added successfully!")
        return redirect('attendance')
    
    return render(request,'add_attedance.html',{'qry':qry})



@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def update_attendance(request, id):
    qry = Student.objects.get(id=id)
    attd = Attendance.objects.filter(stu_rollno=qry)

    if request.method == 'POST':
        if 'a_date' in request.POST:
            a_date = request.POST.get('a_date')
            if Attendance.objects.filter(stu_rollno=qry, date_of_attd=a_date).exists():
                messages.success(request, "Attendance of the selected date exists. Edit it via the form below.")
                return render(request, 'update_attedance.html', {'attd': attd, 'qry': qry, 'date': a_date})
            else:
                messages.error(request, "Attendance of the selected date does not exist.")
                return redirect('update_attendance', id=id)

        else:
            data = request.POST
            status = data.get('attd')
            rollno = data.get('rollno')
            date = data.get('date')

            # Here you should get the attendance object based on the date and student
            attendance_obj = Attendance.objects.get(stu_rollno=qry, date_of_attd=date)

            # Update the attendance status
            attendance_obj.status = status
            attendance_obj.save()
            messages.success(request, "Attendance of student updated!")

            return redirect('attendance')

    return render(request, 'update_attedance.html', {'attd': attd, 'qry': qry})

# def update_attedance(request,id):
     
#      qry=Student.objects.get(id=id)
#      attd=Attendance.objects.filter(stu_rollno=qry)



#      if request.POST.get('a_date'):
#          a_date=request.POST.get('a_date')
#          if Attendance.objects.filter(stu_rollno=qry,date_of_attd=a_date).exists():

#              messages.success(request,"Attendance of selected date  exits edit it via below form..")
#              return render(request,'update_attedance.html',{'attd':attd,'qry':qry})
#          else:
#              messages.error(request,"Attendance of selected date does not exits")
#              return redirect('update_attedance',id=id)

#      if request.method=='POST':
#         data=request.POST
#         status=data.get('attd')
#         rollno=data.get('rollno')
#         # stu_rollno=Student.objects.get(roll_no=rollno)
#         date=data.get('date')

        

#         attd.stu_rollno=qry
#         attd.status=status
#         attd.date_of_attd=date

#         attd.save()
#         return redirect('attendance')

#      return render(request,'update_attedance.html',{'attd':attd,'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def delete_attedance(request,id):

    qry=Student.objects.get(id=id)
    attdd=Attendance.objects.filter(stu_rollno=qry).first()


    if request.POST.get('a_date'):
         
         a_date=request.POST.get('a_date')
         attd=Attendance.objects.filter(stu_rollno=qry,date_of_attd=a_date).exists()
         if attd:
            attdd=Attendance.objects.get(stu_rollno=qry,date_of_attd=a_date)
            attdd.delete()
            messages.success(request,"Attedance of student deleted successfully")
            return redirect('attendance')
         else:
            messages.error(request,"Attedance of student does not exits")
            return redirect('delete_attedance',id=id)
             
    return render(request,'delete_attedance.html')

@login_required(login_url='/login_page/') 
def admin_dash(request): 
    total_fees=Student.objects.filter(fee_status='Paid').aggregate(Sum('fee',default=0)) 
    total_student=Student.objects.all().count() 
    total_teacher=Teacher.objects.all().count() 
    total_upaid_fees=Student.objects.filter(fee_status='Unpaid').aggregate(Sum('fee',default=0)) 
 
 
    data={'total_fees':total_fees['fee__sum'],'total_student':total_student,'total_teacher':total_teacher} 
    return render(request,'admin_dash.html',data)



def contactus(request):
    if request.method=="POST":
        data=request.POST
        name=data.get('name')
        email=data.get('email')
        phone=data.get('phone')
        sub=data.get('subject')
        mess=data.get('mess')

        ContactUs.objects.create(name=name,email=email,number=phone,subject=sub,message=mess)

        return redirect('contactus')
    return render(request,'contactus.html')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def view_contactus(request):
    qry=ContactUs.objects.all()
    return render(request,'view_contactus.html',{'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def replay_contactus(request,id):
    qry=ContactUs.objects.get(id=id)

    if request.method=='POST':
        sub=request.POST.get('sub')
        mess=request.POST.get('mess')

        send_mail(subject=sub,recipient_list=[qry.email],message=mess,from_email='gohelgau@gmail.com',fail_silently=False)
       
        
        if send_mail:
            messages.success(request,"Mail Sent Successfully!")
            qry.delete()
            return redirect('view_contactus')
        
    return render(request,'replay_contactus.html')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_subject(request):
    sub = Subject.objects.all()
    paginator = Paginator(sub, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    cls = Class.objects.all()

    if request.method == 'POST':
        sub_name = request.POST.get('sub')
        medium = request.POST.get('medium')
        cls_id = request.POST.get('class')
        cls_name = Class.objects.get(id=cls_id)

        # Validate subject name length
        if len(sub_name.strip()) < 2:
            messages.error(request, "Subject name must be at least 2 characters long.")
            return redirect('add_subject')

        # Save the subject data
        qry = Subject.objects.create(sub_name=sub_name, cls_name=cls_name, medium_name=medium)
        qry.save()

        messages.success(request,"Subject Added successfully")
        return redirect('add_subject')
    return render(request,'add_subject.html',{'sub':page_obj,'cls':cls})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def update_subject(request, id):
    qry = Subject.objects.get(id=id)
    cls = Class.objects.all()

    if request.method == 'POST':
        sub = request.POST.get('sub')
        medium = request.POST.get('medium')
        cls_id = request.POST.get('class')
        cls_name = Class.objects.get(id=cls_id)

        # Validate subject name length
        if len(sub.strip()) < 2:
            messages.error(request, "Subject name must be at least 2 characters long.")
            return redirect('update_subject', id=id)

        qry.sub_name = sub
        qry.medium_name = medium
        qry.cls_name = cls_name

        qry.save()
        messages.success(request,"Subject updated successfull")
        return redirect ('add_subject')

    return render(request,'update_subject.html',{'sub':qry,'cls':cls})


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_subject(request,id):
    qry=Subject.objects.get(id=id)
    qry.delete()
    messages.success(request,"Subject deleted succesfully")
    return redirect('add_subject')


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def create_user(request):
    all_user=User.objects.exclude(username="admin")
    paginator = Paginator(all_user, 8)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.POST.get('search'):
        search=request.POST.get('search')
        page_obj=all_user.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(username__icontains=search) |
            Q(email__icontains=search) 
        )
        data={'all_user':page_obj}
        return render(request,'create_user.html',data)


    if request.method=='POST':
        if request.POST.get('parent'):
         parent=Parent.objects.all()
         for i in parent:
            fname=i.fname
            lname=i.lname
            email=i.email
            phone=i.phone_no
            existing_user=User.objects.filter(username=email).first()

            if existing_user:
                continue

            hass_pass=make_password(phone)
            p_user=User.objects.create(username=email,password=hass_pass,email=email,first_name=fname,last_name=lname)
            p_user.groups.add(Group.objects.get(name='parent'))
            x=Parent_user.objects.create(parent_user=p_user)
            x.save()

            i.p_user=x
            i.save()
            messages.success(request,"Parent accounts created successfully!")
            return redirect("create_user")

        
        
        elif request.POST.get('teacher'):
            teacher=Teacher.objects.all()
            
            for i in teacher:
                email=i.email
                phone=i.phone_no
                fname=i.fname
                lname=i.lname
                existing_user=User.objects.filter(username=email).first()

                if existing_user:
                    continue
                hase_password=make_password(phone)
                t_user=User.objects.create(username=email,password=hase_password,email=email,first_name=fname,last_name=lname)
                t_user.groups.add(Group.objects.get(name='teacher'))
                x=Teacher_user.objects.create(teacher_user=t_user)
                x.save()

                i.t_user=x
                i.save()
                messages.success(request,"Teacher accounts created successfully!")
                return redirect("create_user")

    data={'all_user':page_obj}
    return render(request,'create_user.html',data)


# def create_user(request):
#     all_user=User.objects.exclude(username="admin")
#     paginator = Paginator(all_user, 8)  
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     if request.method == 'POST':
#         selected_group = request.POST.get('group', 'all')  # Default to 'all' if no selection

#         if selected_group == 'parent':
#             all_user =User.objects.filter(groups__name='parent').order_by('id')
#         elif selected_group == 'teacher':
#             all_user =User.objects.filter(groups__name='teacher').order_by('id')
#         else:
#             all_user=User.objects.exclude(username='admin').order_by('id')

#         return render(request,'create_user.html',{'all_user':all_user})
    

#     if request.POST.get('search'):
#         search=request.POST.get('search')
#         all_user=all_user.filter(
#             Q(first_name__icontains=search) |
#             Q(last_name__icontains=search) |
#             Q(username__icontains=search) |
#             Q(email__icontains=search) 
#         )
#         data={'all_user':all_user}
#         return render(request,'create_user.html',data)


#     if request.method=='POST':
#         if request.POST.get('parent'):
#          parent=Parent.objects.all()
#          print(parent)
#          for i in parent:
#             fname=i.fname
#             lname=i.lname
#             email=i.email
#             phone=i.phone_no
#             existing_user=User.objects.filter(username=email).first()

#             if existing_user:
#                 continue

#             hass_pass=make_password(phone)
#             p_user=User.objects.create(username=email,password=hass_pass,email=email,first_name=fname,last_name=lname)
#             p_user.groups.add(Group.objects.get(name='parent'))
#             x=Parent_user.objects.create(parent_user=p_user)
#             x.save()

#             i.p_user=x
#             i.save()
        
        
#         elif request.POST.get('teacher'):
#             teacher=Teacher.objects.all()
            
#             for i in teacher:
#                 email=i.email
#                 phone=i.phone_no
#                 fname=i.fname
#                 lname=i.lname
#                 existing_user=User.objects.filter(username=email).first()

#                 if existing_user:
#                     continue
#                 hase_password=make_password(phone)
#                 t_user=User.objects.create(username=email,password=hase_password,email=email,first_name=fname,last_name=lname)
#                 t_user.groups.add(Group.objects.get(name='teacher'))
#                 x=Teacher_user.objects.create(teacher_user=t_user)
#                 x.save()

#                 i.t_user=x
#                 i.save()

#     data={'all_user':page_obj}
#     return render(request,'create_user.html',data)


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def view_parent_teacher(request):
    parent=Parent.objects.all()
    teacher=Teacher.objects.all()
    data={'parent':parent,'teacher':teacher}
    return render(request,'view_parent_teacher.html',data)

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_user(request,id):
    qry=User.objects.get(id=id)
    qry.delete()
    return redirect('create_user')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_parent(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Validate first name and last name
        if len(fname.strip()) < 2 or len(lname.strip()) < 2:
            messages.error(request, "First name and last name must be at least 2 characters long.")
            return redirect('add_parent')

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect('add_parent')

        # Validate phone number
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must consist of exactly 10 digits.")
            return redirect('add_parent')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email address is already in use.")
            return redirect('add_parent')

        x = Parent(fname=fname, lname=lname, email=email, phone_no=phone)
        x.save()
        messages.success(request,"Parent Added successfully!")

        return redirect('create_user')
    return render(request,'add_parent.html')



@login_required(login_url='/login_page')
@user_passes_test(is_superuser)

def add_teacher(request):
    if request.method == 'POST':
        img = request.FILES.get('img')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        salary = request.POST.get('salary')
        dob = request.POST.get('dob')
        doj = request.POST.get('doj')
        expr = request.POST.get('expr')

        # UG Details
        if 'ugToggle' in request.POST:
            ug_uni_name = request.POST.get('ugUniName')
            ug_degree_name = request.POST.get('ugDegreeName')
            ug_overall_cgpa = request.POST.get('ugOverallCGPA')
        else:
            ug_uni_name = ug_degree_name = ug_overall_cgpa = None

        # PG Details
        if 'pgToggle' in request.POST:
            pg_uni_name = request.POST.get('pgUniName')
            pg_degree_name = request.POST.get('pgDegreeName')
            pg_overall_cgpa = request.POST.get('pgOverallCGPA')
        else:
            pg_uni_name = pg_degree_name = pg_overall_cgpa = None

        # Validate first name and last name
        if len(fname.strip()) < 2 or len(lname.strip()) < 2:
            messages.error(request, "First name and last name must be at least 2 characters long.")
            return redirect('add_teacher')

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect('add_teacher')

        # Validate phone number
        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Phone number must consist of exactly 10 digits.")
            return redirect('add_teacher')

        # Validate experience
        try:
            expr = int(expr)
            if expr < 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Experience must be a non-negative integer.")
            return redirect('add_teacher')
        
        # Validate image upload
        if not img or not img.content_type.startswith('image'):
            messages.error(request, 'Please upload a valid image file.')
            return redirect('add_teacher')

        # Save teacher data
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email address is already in use.")
            return redirect('add_teacher')

        x = Teacher.objects.create(
            fname=fname, lname=lname, gender=gender, email=email, phone_no=phone, dob=dob, doj=doj,
            expr=expr, address=address, ug_uni_name=ug_uni_name, ug_degree_name=ug_degree_name,
            ug_overall_cgpa=ug_overall_cgpa, pg_uni_name=pg_uni_name, pg_degree_name=pg_degree_name,
            pg_overall_cgpa=pg_overall_cgpa, teacher_img=img, salary=salary
        )
        x.save()
        messages.success(request,"Teacher Added successfully!")
        
        return redirect('create_user')
    return render(request,'add_teacher.html')

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def view_teacher(request,id):
    qry=Teacher.objects.filter(id=id)
    return render(request,'update_teacher.html',{'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_curriculum(request):
    cls = Class.objects.all()
    if request.method == "POST":
        pdf = request.FILES.get('pdf')
        medium = request.POST.get('medium')
        cls_id = request.POST.get('class')
        cls_name = get_object_or_404(Class, id=cls_id)

        # Check if a PDF file is uploaded
        if not pdf:
            messages.error(request, "No PDF file uploaded.")
            return redirect('add_curriculum')

        # Check if the uploaded file is a PDF
        ext = os.path.splitext(pdf.name)[1]
        if ext.lower() != '.pdf':
            messages.error(request, "Only PDF files are allowed.")
            return redirect('add_curriculum')

        # Check if a curriculum for the same class and medium already exists
        existing_curriculum = Curriculum.objects.filter(cls_name=cls_name, medium_name=medium).exists()
        if existing_curriculum:
            messages.error(request, "A curriculum for this class and medium already exists.")
            return redirect('add_curriculum')

        # Save the curriculum data
        x = Curriculum.objects.create(pdf=pdf, cls_name=cls_name, medium_name=medium)
        x.save()
        return redirect('add_curriculum')
    qry=Curriculum.objects.all()
        
    return render(request,'add_curriculum.html',{'cls':cls,'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def update_curriculum(request,id):
    cls=Class.objects.all()
    qry=Curriculum.objects.get(id=id)
    if request.method=="POST":
        pdf=request.FILES.get('pdf')
        medium=request.POST.get('medium')
        cls_id=request.POST.get('class')
        cls_name=Class.objects.get(id=cls_id)

        if pdf:
            qry.pdf=pdf
        qry.cls_name=cls_name
        qry.medium_name=medium

        if pdf:
            ext = os.path.splitext(pdf.name)[1]
            if ext.lower() != '.pdf':
                messages.error(request, "Only PDF files are allowed.")
                return redirect('add_curriculum')  

        else:
            messages.error(request, "No PDF file uploaded.")
            return redirect('add_curriculum')

        qry.save()
        return redirect('add_curriculum')
    
    return render(request,'update_curriculum.html',{'cls':cls})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_curriculum(request,id):
    qry=Curriculum.objects.get(id=id)
    qry.delete()
    return redirect('add_curriculum')

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def add_ptm(request):
    cls = Class.objects.all()

    if request.method == "POST":
        data = request.POST
        topic = data.get('topic')
        desc = data.get('desc')
        date = data.get('date')
        time = data.get('time')
        medium = request.POST.get('medium')
        cls_id = request.POST.get('class')
        cls_name = Class.objects.get(id=cls_id)

        # Check if a PTM with the same class, medium, date, and time already exists
        #existing_ptm = PTM.objects.filter(cls_name=cls_name, medium_name=medium, ptm_date=date, ptm_time=time)
        existing_ptm = PTM.objects.filter(cls_name=cls_name, medium_name=medium, ptm_date=date)
        if existing_ptm.exists():
            messages.error(request, "A PTM for the selected class & medium already exists  on this date.")
            return redirect('add_ptm')

         # Validate PTM time (between 9 am to 3 pm)
        #input_time = datetime.strptime(time, '%H:%M').time()
        #   messages.error(request, "PTM time must be between 9 am and 3 pm.")
            return redirect('add_ptm')

        # Save new PTM
        x = PTM.objects.create(topic=topic, desc=desc, ptm_date=date, ptm_time=time, cls_name=cls_name, medium_name=medium)
        x.save()
        messages.error(request, "PTM added successfully!")
        return redirect('add_ptm')
    qry=PTM.objects.all()
    return render(request,'add_ptm.html',{'cls':cls,'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def update_ptm(request,id):
    cls=Class.objects.all()
    qry=PTM.objects.get(id=id)
    if request.method=="POST":
        data=request.POST
        topic=data.get('topic')
        desc=data.get('desc')
        date=data.get('date')
        time=data.get('time')
        medium=request.POST.get('medium')
        cls_id=request.POST.get('class')
        cls_name=Class.objects.get(id=cls_id)

        input_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Get today's date
        today_date = timezone.now().date()
        # Validate date
        if input_date < today_date:
            # Handle invalid date here, e.g., return an error message or render a template with error information
            messages.error(request,"Selected date cannot be before today's date!")
            return redirect('add_ptm')
        else:
            # Process valid dataparent_update_detailsparent_update_detailsparent_update_detailsparent_update_detailsparent_update_details
            # Your processing logic hereZZZ
            pass



        qry.topic=topic
        qry.desc=desc
        qry.ptm_date=date
        qry.ptm_time=time
        qry.medium_name=medium
        qry.cls_name=cls_name
        qry.save()
        messages.error(request, "PTM updated successfully!")
        return redirect('add_ptm')

    return render(request,'update_ptm.html',{'cls':cls,'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def delete_ptm(request,id):
    qry=PTM.objects.get(id=id)
    qry.delete()
    messages.error(request, "PTM deleted successfully!")
    return redirect('add_ptm')

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def teacher_add_marks(request):
    cls=Class.objects.all()
    if request.method=="POST":
       
        medium=request.POST.get('medium')
        cls_id=request.POST.get('class')
        cls_name=Class.objects.get(id=cls_id)
        qry=Student.objects.filter(medium_name=medium,cls_name=cls_name)


        return render(request,'teacher_add_marks.html',{'qry':qry,'cls':cls})
    data={'cls':cls}
    return render(request,'teacher_add_marks.html',data)

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def add_marks(request, id):
    student = Student.objects.get(id=id)
    medium = student.medium_name
    cls = student.cls_name
    sub = Subject.objects.filter(medium_name=medium, cls_name=cls)
    sub_count = Subject.objects.filter(medium_name=medium, cls_name=cls).count()

    if request.method == 'POST':
        marks_list = []
        total_obtained_marks = 0

        for subject in sub:
            marks_obtained = request.POST.get(subject.sub_name)
            if marks_obtained and int(marks_obtained) >= 0:
                total_obtained_marks += int(marks_obtained)
            else:
                messages.error(request, "Marks must be positive numbers.")
                return redirect('add_marks', id=id)

        exam = request.POST.get('exam')
        date = request.POST.get('e_date')
        existing_marks = Marks.objects.filter(student=student, exam=exam)
        if existing_marks.exists():
            messages.error(request, f"Marks for {exam} exam already exist for this student.")
            return redirect('add_marks', id=id)

        # Calculate total marks based on the count of subjects
        total_marks = sub_count * 50

        # Calculate grade based on total obtained marks
        grade = calculate_grade(total_obtained_marks, total_marks)

        # Create Marks objects for each subject
        for subject in sub:
            marks_obtained = request.POST.get(subject.sub_name)
            marks = Marks(student=student,
                          subject=subject,
                          marks_obtained=marks_obtained,
                          total_marks=total_marks,
                          exam_date=date,
                          exam=exam,
                          total_marks_obtained=total_obtained_marks,
                          grade=grade)
            marks_list.append(marks)

        # Bulk create Marks objects
        Marks.objects.bulk_create(marks_list)

        messages.error(request, "Marks added successfully!")
        return redirect('teacher_add_marks')

    return render(request, 'add_marks.html', {'sub': sub})

def calculate_grade(total_obtained_marks, total_marks):
    if total_marks > 0:
        # Calculate percentage
        percentage = (total_obtained_marks / total_marks) * 100

        # Define your grading system here based on percentage
        # For example:
        if percentage >= 90:
            return 'A+'
        elif 80 <= percentage < 90:
            return 'A'
        elif 70 <= percentage < 80:
            return 'B+'
        elif 60 <= percentage < 70:
            return 'B'
        elif 50 <= percentage < 60:
            return 'C'
        else:
            return 'F'
    else:
        return 'F'  


@login_required(login_url='/login_page')
@user_passes_test(is_teacher)

def update_marks(request, id):
    student = Student.objects.get(id=id)
    medium = student.medium_name
    cls = student.cls_name
    sub = Subject.objects.filter(medium_name=medium, cls_name=cls)
    sub_count = Subject.objects.filter(medium_name=medium, cls_name=cls).count()
    
    if request.POST.get('exam'):
        exam = request.POST.get('exam')
        
        # Check if marks exist for the specified exam and student
        marks = Marks.objects.filter(exam=exam, student=student)
        if not marks.exists():
            messages.info(request, "No marks found for this student.")
            return redirect('update_marks', id=id)
        
        # Render the template with the existing marks for update
        return render(request, 'update_marks.html', {'marks': marks})
    
    if request.method == 'POST':
        # Process the updated marks
        for subject in sub:
            marks_obtained = request.POST.get(subject.sub_name)
            exam = request.POST.get('exam1')
            date = request.POST.get('e_date')
            
            # Get the mark object for the subject and exam
            mark = Marks.objects.filter(subject=subject, exam=exam, student=student).first()
            
            if marks_obtained:
                # Validate marks within the range of 0 to 50
                try:
                    marks_obtained = float(marks_obtained)
                    if marks_obtained < 0 or marks_obtained > 50:
                        messages.error(request, "Marks must be between 0 and 50.")
                        return redirect('update_marks', id=id)
                except ValueError:
                    messages.error(request, "Invalid marks value.")
                    return redirect('update_marks', id=id)
                
                # Save the marks
                mark.marks_obtained = marks_obtained
                mark.exam_date = date
                mark.exam = exam
                mark.total_marks = sub_count * 50
                mark.save()
        
        # Fetch the marks again after updating them
        marks = Marks.objects.filter(exam=exam, student=student)
        
        # Recalculate total obtained marks and grade
        total_obtained_marks = sum(float(mark.marks_obtained) for mark in marks)
        total_marks = sub_count * 50
        grade = calculate_grade(total_obtained_marks, total_marks)
        
        # Update the marks object with new total obtained marks and grade
        marks.update(total_marks_obtained=total_obtained_marks, grade=grade)
        
        messages.success(request, "Marks updated successfully")
        return redirect('teacher_add_marks')
    
    return render(request, 'update_marks.html', {'sub': sub})

def delete_marks(request,id): 
    student=Student.objects.get(id=id) 
    if request.method=='POST': 
        exam=request.POST.get('exam') 
        qry=Marks.objects.filter(student=student,exam=exam) 
 
        if not qry.exists(): 
            messages.info(request, "No marks exist for this student and exam.") 
        else: 
            qry.delete() 
            messages.success(request, f"Marks for exam {exam} deleted successfully.") 
        return redirect('teacher_add_marks') 
 

    return render(request,'delete_marks.html')

def change_password_s(request): 
    if request.method == 'POST': 
        form = PasswordChangeForm(request.POST) 
        if form.is_valid(): 
            new_password = form.cleaned_data['new_password'] 
            # Change the superuser's password 
            superuser = User.objects.get(username='admin')  # Replace 'superuser' with the actual username 
            superuser.set_password(new_password) 
            superuser.save() 
            return redirect('login_page')  # Redirect to a success page 
    else: 
        form = PasswordChangeForm()
    return render(request, 'change_password_s.html', {'form': form})


@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def add_timetable(request):
    cls = Class.objects.all()
    if request.method == "POST":
        pdf = request.FILES.get('pdf')
        medium = request.POST.get('medium')
        cls_id = request.POST.get('class')
        cls_name = get_object_or_404(Class, id=cls_id)

        # Check if a PDF file is uploaded
        if not pdf:
            messages.error(request, "No PDF file uploaded.")
            return redirect('add_timetable')

        # Check if the uploaded file is a PDF
        ext = os.path.splitext(pdf.name)[1]
        if ext.lower() != '.pdf':
            messages.error(request, "Only PDF files are allowed.")
            return redirect('add_timetable')

        # Check if a curriculum for the same class and medium already exists
        existing_curriculum = Timetable.objects.filter(cls_name=cls_name, medium_name=medium).exists()
        if existing_curriculum:
            messages.error(request, "A timetable for this class and medium already exists.")
            return redirect('add_timetable')

        # Save the curriculum data
        x = Timetable.objects.create(pdf=pdf, cls_name=cls_name, medium_name=medium)
        x.save()
        messages.error(request, "Time table added sucessfully!")
        return redirect('add_timetable')
    qry=Timetable.objects.all()

    return render(request,'add_timetable.html',{'qry':qry,'cls':cls})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def update_timetable(request,id):
    cls=Class.objects.all()
    qry=Timetable.objects.get(id=id)
    if request.method=="POST":
        pdf=request.FILES.get('pdf')
        medium=request.POST.get('medium')
        cls_id=request.POST.get('class')
        cls_name=Class.objects.get(id=cls_id)

        if pdf:
            qry.pdf=pdf
        qry.cls_name=cls_name
        qry.medium_name=medium

        if pdf:
            ext = os.path.splitext(pdf.name)[1]
            if ext.lower() != '.pdf':
                messages.error(request, "Only PDF files are allowed.")
                return redirect('update_timetable',id=id)  

        else:
            messages.error(request, "No PDF file uploaded.")
            return redirect('update_timetable',id=id)

        qry.save()
        messages.success(request,"Timetable updated successully!")
        return redirect('add_timetable')
    return render(request,'update_timetable.html',{'qry':qry,'cls':cls})

@login_required(login_url='/login_page')
@user_passes_test(is_superuser)
def delete_timetable(request,id):
    qry=Timetable.objects.get(id=id)
    qry.delete()
    return redirect('add_timetable')


def view_timetable(request):
    timetable=Timetable.objects.filter(sub__cls_name=1,sub__medium_name='English')

    return render(request,'view_timetable.html',{'timetable':timetable})

@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_add_details(request):
     parent_user = Parent_user.objects.get(parent_user=request.user)
     parent = Parent.objects.filter(p_user=parent_user)
     return render(request,'parent_add_details.html',{'parent': parent})

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def teacher_view_details(request):
    user = Teacher_user.objects.get(teacher_user=request.user)  
    teacher=Teacher.objects.filter(t_user=user)
    print(teacher)
    return render(request,'teacher_view_details.html',{'teacher':teacher})

@login_required(login_url='/login_page')
@user_passes_test(is_teacher)
def teacher_update_details(request,id): 
    qry=Teacher.objects.get(id=id) 
 
    if request.method == 'POST': 
        teacher_img = request.FILES.get('img') 
        fname = request.POST.get('fname') 
        lname = request.POST.get('lname') 
        gender = request.POST.get('gender') 
        email = request.POST.get('email') 
        phone_no = request.POST.get('phone')
        address=request.POST.get('address') 
 
        if teacher_img: 
            qry.teacher_img=teacher_img 
        qry.fname=fname 
        qry.lname=lname 
        qry.email=email 
        qry.gender=gender 
        qry.phone_no=phone_no 
        qry.address=address
 
        qry.save() 
        messages.success(request,"Profile updated successfully!")
        return redirect('teacher_view_details')
    return render(request,'teacher_update_details.html',{'qry':qry})

@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def quiz(request):
    return render(request,'quiz.html')

@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_update_details(request, id): 
    qry = Parent.objects.get(id=id) 

    if request.method == 'POST': 
        parent_img = request.FILES.get('img') 
        fname = request.POST.get('fname') 
        lname = request.POST.get('lname') 
        gender = request.POST.get('gender') 
        email = request.POST.get('email') 
        phone_no = request.POST.get('phone')
        address = request.POST.get('address')

        # Validate first name and last name
        if len(fname.strip()) < 2 or len(lname.strip()) < 2:
            messages.error(request, "First name and last name must be at least 2 characters long.")
            return render(request, 'parent_update_details.html', {'qry': qry})

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'parent_update_details.html', {'qry': qry})

        # Validate image upload
        if parent_img:
            if not parent_img.content_type.startswith('image'):
                messages.error(request, "Only image files are allowed.")
                return render(request, 'parent_update_details.html', {'qry': qry})
            qry.parent_img = parent_img
        else:
            messages.error(request, 'Please upload an image file.')
            return render(request, 'parent_update_details.html', {'qry': qry})

        # Validate phone number length
        if len(phone_no) != 10:
            messages.error(request, "Phone number must consist of exactly 10 digits.")
            return render(request, 'parent_update_details.html', {'qry': qry})


        qry.fname = fname 
        qry.lname = lname 
        qry.email = email 
        qry.gender = gender 
        qry.phone_no = phone_no 
        qry.address = address

        qry.save() 
        messages.success(request,"Profile updated successfully!")
        return redirect('parent_add_details')
    return render(request,'parent_update_details.html',{'qry':qry})


@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_view_student(request): 
     students = Student.objects.filter(parent__p_user__parent_user=request.user) 
     return render(request,'parent_view_student.html',{'students':students}) 
  
@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_view_marks(request): 
    students = Student.objects.filter(parent__p_user__parent_user=request.user) 
    semester_1_marks = Marks.objects.filter(student__in=students, exam='Semester-1')
    semester_2_marks = Marks.objects.filter(student__in=students, exam='Semester-2')
    return render(request, 'parent_view_marks.html', {'students': students, 'semester_1_marks': semester_1_marks, 'semester_2_marks': semester_2_marks})
   


@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_view_attendance(request): 

    students = Student.objects.filter(parent__p_user__parent_user=request.user) 
    attendance=Attendance.objects.filter(stu_rollno__in=students) 
    paginator = Paginator(attendance, 25)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if request.method=='POST':
        date=request.POST.get('date')

        attendance=attendance.filter(
            Q(date_of_attd__icontains=date)
        )
        return render(request,'parent_view_attendance.html',{'attendance':attendance}) 
    return render(request,'parent_view_attendance.html',{'attendance':page_obj}) 

@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_view_timetable(request): 
    students = Student.objects.filter(parent__p_user__parent_user=request.user) 
    timetable = Timetable.objects.filter(cls_name__in=[student.cls_name for student in students], 
                                    medium_name__in=[student.medium_name for student in students]) 
 
    return render(request,'parent_view_timetable.html',{'timetable':timetable}) 

@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_view_ptm(request): 
    students = Student.objects.filter(parent__p_user__parent_user=request.user) 
    qry=PTM.objects.filter(cls_name__in=[student.cls_name for student in students], 
                                    medium_name__in=[student.medium_name for student in students]) 
    return render(request,'parent_view_ptm.html',{'qry':qry}) 
@login_required(login_url='/login_page')
@user_passes_test(is_parent)
def parent_view_curriculum(request): 
    students = Student.objects.filter(parent__p_user__parent_user=request.user) 
    qry = Curriculum.objects.filter(cls_name__in=[student.cls_name for student in students], 
                                    medium_name__in=[student.medium_name for student in students]) 
    return render(request, 'parent_view_curriculum.html', {'qry': qry})


@login_required(login_url='/login_page')
@user_passes_test(is_parent)

def progress_chart(request):
    students = Student.objects.filter(parent__p_user__parent_user=request.user)
    marks_data = Marks.objects.filter(student__in=students)
    progress_data = defaultdict(lambda: defaultdict(list))
    num_students = students.count()  # Count the number of students
    
    if num_students < 2:  # Execute if there is only one student
        for mark in marks_data:
            student_name = mark.student.fname  # Assuming there's a 'fname' field in the Student model
            semester = mark.exam
            total_marks_obtained = mark.total_marks_obtained  
            total_marks = mark.total_marks
            progress = (total_marks_obtained / total_marks) * 100 if total_marks != 0 else 0  
            
            progress_data[student_name][semester].append(progress)
        
        fig, ax = plt.subplots()
        semesters = set()
        for student_name, semesters_data in progress_data.items():
            for semester, progress_list in semesters_data.items():
                avg_progress = sum(progress_list) / len(progress_list)
                ax.bar(semester, avg_progress, label=f"{student_name} ({semester})")
                semesters.add(semester)

        ax.set_xlabel('Semester')
        ax.set_ylabel('Average Progress (%)')
        ax.set_title('Average Progress of Students in Each Semester')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend position
        
        # Arrange x-axis ticks with all semesters
        ax.set_xticks(range(len(semesters)))
        ax.set_xticklabels(semesters)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')

    else:  # Execute if there are multiple students
        for mark in marks_data:
            student_name = mark.student.fname  # Assuming there's a 'fname' field in the Student model
            semester = mark.exam
            total_marks_obtained = mark.total_marks_obtained  
            total_marks = mark.total_marks
            progress = (total_marks_obtained / total_marks) * 100 if total_marks != 0 else 0  
            
            progress_data[student_name][semester].append(progress)
        
        fig, ax = plt.subplots()
        semesters = sorted(set().union(*(semesters_data.keys() for semesters_data in progress_data.values())))
        width = 0.35  # Width of the bars
        x = np.arange(len(semesters))  # X positions for the groups of bars
        
        for i, (student_name, semesters_data) in enumerate(progress_data.items()):
            progress_values = [sum(semesters_data.get(semester, [])) / len(semesters_data.get(semester, [])) for semester in semesters]
            ax.bar(x + i * width, progress_values, width, label=student_name)

        ax.set_xlabel('Semester')
        ax.set_ylabel('Average Progress (%)')
        ax.set_title('Average Progress of Students in Each Semester')
        ax.set_xticks(x + width * (len(progress_data) - 1) / 2)
        ax.set_xticklabels(semesters)

        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))  # Adjust legend position

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')

    # Convert plot to bytes
    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    # Embed the image in HTML
    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'progress_chart.html', {'graphic': graphic})

import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_fee_report_pdf(request):
    students = Student.objects.all()
    school_logo = 'static/ss school report frunt.jpg'
    # Prepare data to pass to the template
    context = {
        'fees_data': students,
        'current_datetime': datetime.datetime.now(),
        'title': 'Fee Report',  # Title for the report
        'school_logo': school_logo,
    }

    # Render template
    template = get_template('fee_report_template.html')
    html = template.render(context)



    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="fee_report.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

def class_teacher(request): 
    cls=Class.objects.all() 
    teacher=Teacher.objects.all() 
 
    if request.method=="POST": 
        m=request.POST.get('medium') 
        cls_id=request.POST.get('class') 
        cls_name=Class.objects.get(id=cls_id) 
        t=request.POST.get('te') 
        t1=Teacher.objects.get(id=t) 
 
        x=Teacher_has_class.objects.create(cls_name=cls_name,medium_name=m,cls_teacher=t1) 
        x.save() 
        messages.success(request,"Teacher Added to the class!") 
        return redirect('class_teacher') 
     
    qry=Teacher_has_class.objects.all() 
    data={'cls':cls,'teacher':teacher,'qry':qry} 
    return render(request,"class_teacher.html",data) 
 
def update_class_teacher(request,id): 
 
    qry=Teacher_has_class.objects.get(id=id) 
    cls=Class.objects.all() 
    teacher=Teacher.objects.all() 
 
    if request.method=="POST": 
        m=request.POST.get('medium') 
        cls_id=request.POST.get('class') 
        cls_name=Class.objects.get(id=cls_id) 
        t=request.POST.get('te') 
        t1=Teacher.objects.get(id=t) 
 
        qry.medium_name=m 
        qry.cls_name=cls_name 
        qry.cls_teacher=t1 
 
        qry.save() 
        messages.success(request,"Class teacher update successfully!")
        return redirect('class_teacher') 
 
    data={'cls':cls,'teacher':teacher,'qry':qry} 
    return render(request,'update_class_teacher.html',data) 
 
 
def delete_class_teacher(request,id): 
    qry=Teacher_has_class.objects.get(id=id) 
    qry.delete() 
    return redirect('class_teacher')



def generate_attendance_report_pdf(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        if month and year:
            return generate_attendance_report_pdf_month_year(request, month, year)

    # Render the form HTML if not POST request or missing month/year in POST data
    return render(request, 'report_form.html')

def generate_attendance_report_pdf_month_year(request, month, year):
    # Convert month and year to integers
    month = int(month)
    year = int(year)

    # Get attendance data for the specified month and year
    attendance_data = Attendance.objects.filter(date_of_attd__month=month, date_of_attd__year=year)
    school_logo = 'static/ss school report frunt.jpg'

    # Dictionary to store attendance statistics for each student
    student_attendance_stats = {}

    # Calculate attendance statistics for each student
    for attendance in attendance_data:
        roll_no = attendance.stu_rollno.roll_no
        if roll_no not in student_attendance_stats:
            student_attendance_stats[roll_no] = {
                'name': attendance.stu_rollno.fname + ' ' + attendance.stu_rollno.lname,
                'medium': attendance.stu_rollno.medium_name,
                'class_name': attendance.stu_rollno.cls_name,
                'present_days': 0,
                'roll_no': roll_no
            }
        if attendance.status == 'Present':
            student_attendance_stats[roll_no]['present_days'] += 1

    # Prepare data to pass to the template
    context = {
        'attendance_stats': student_attendance_stats.values(),
        'month': month,
        'year': year,
        'title': f'Attendance Report - {month}/{year}',
        'current_datetime': datetime.datetime.now(),
        'school_logo': school_logo,
    }

    # Render template
    template = get_template('attendance_report_template.html')
    html = template.render(context)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="attendance_report_{month}_{year}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

def generate_marks_report_pdf(request): 
    # Fetch mark data 
    marks_data = Marks.objects.select_related('student').all() 
    school_logo = 'static/ss school report frunt.jpg' 
 
 
    student_marks = {} 
 
    # Prepare data to pass to the template 
    for mark in marks_data: 
        student_id = mark.student.id 
        if student_id not in student_marks: 
            student_marks[student_id] = { 
                'student': mark.student, 
                'semesters': {}, 
                'class': mark.student.cls_name.c_name, 
                'medium': mark.student.medium_name, 
            } 
        if mark.exam not in student_marks[student_id]['semesters']: 
            student_marks[student_id]['semesters'][mark.exam] = { 
                'total_marks': 0, 
                'total_marks_obtained': 0, 
                'marks': [], 
            } 
        if mark.total_marks is not None: 
            student_marks[student_id]['semesters'][mark.exam]['total_marks'] = mark.total_marks 
        if mark.marks_obtained is not None: 
            student_marks[student_id]['semesters'][mark.exam]['total_marks_obtained'] += mark.marks_obtained 
        student_marks[student_id]['semesters'][mark.exam]['marks'].append(mark) 
    # Prepare data to pass to the template 
    context = { 
        'marks_data': marks_data, 
        'title': 'Marks Report', 
        'current_datetime': datetime.datetime.now(), 
        'school_logo': school_logo, 
        'student_marks': student_marks.values(), 
    } 
 
    # Render template 
    template = get_template('marks_report_template.html') 
    html = template.render(context) 
 
    # Create a PDF 
    response = HttpResponse(content_type='application/pdf') 
    response['Content-Disposition'] = 'filename="marks_report.pdf"' 
 
    # Generate PDF 
    pisa_status = pisa.CreatePDF(html, dest=response) 
    if pisa_status.err: 
        return HttpResponse('We had some errors <pre>' + html + '</pre>') 
 
    return response
