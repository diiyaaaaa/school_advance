

# Create your models here.

from django.db import models
from datetime import date
from django.contrib.auth.models import User , Group

teacher, created=Group.objects.get_or_create(name='teacher') 
parent, created=Group.objects.get_or_create(name='parent') 
# Create your models here.

'''class Medium(models.Model):
    m_name=models.CharField(max_length=30)'''

class Class(models.Model):
    c_name=models.CharField(max_length=30)
    
    def __str__(self) -> str:
        return self.c_name


class Student(models.Model):
    Medium=[('English','English'),('Gujarati','Gujarati')]
    gn=[('Boy','Boy'),('Girl','Girl')]
    stu_img=models.ImageField(upload_to='students/',default='')
    roll_no=models.PositiveIntegerField(default=None,null=True)
    enroll_date=models.DateField()
    fname=models.CharField(max_length=30)
    lname=models.CharField(max_length=30)
    dob=models.DateField(null=True)
    gender=models.CharField(max_length=15,choices=gn,default='')
    address=models.TextField(default='Ahemdabad')
    cls_name=models.ForeignKey('Class',on_delete=models.CASCADE,default='')
    medium_name=models.CharField(max_length=30,choices=Medium,default='English')
    fee=models.PositiveIntegerField(null=True)
    fee_status=models.CharField(max_length=20,choices=[('Paid','Paid'),('Unpaid','Unpaid')],default='Unpaid',null=True)
    phone_no=models.CharField(max_length=20,default=None,null=True)
    acd_year=models.CharField(max_length=20,null=True)
    parent=models.ForeignKey('Parent',on_delete=models.CASCADE,null=True)

    class Meta:
        ordering =['roll_no']

    def __str__(self) -> str:
        return f'{self.fname} - {self.cls_name} - {self.medium_name}' 

class Gallery(models.Model):
    img=models.ImageField(upload_to='gallery/')
    img_desc=models.TextField()

class Activity(models.Model):
    act_img=models.ImageField(upload_to='activity/')
    act_name=models.CharField(max_length=120)
    act_desc=models.TextField()
    date=models.DateField(null=True)

    def save(self, *args, **kwargs):
        # Assuming month_year is in the format "YYYY-MM"
        # Convert it to the first day of the month
        if self.date:
            self.date = self.date + "-01"
        super().save(*args, **kwargs)

class Attendance(models.Model):
    ch=[('Present','Present'),('Absent','Absent')]
    stu_rollno=models.ForeignKey('Student',on_delete=models.CASCADE,default=1)
    status=models.CharField(max_length=20,choices=ch,default='Absent')
    date_of_attd=models.DateField(default=date.today)

    def __str__(self) -> str:
        return f"Attendance of {self.stu_rollno} is {self.status}"
    

g=[('Male','Male'),('Female','Female')]   
class Teacher(models.Model):
    t_user=models.OneToOneField('Teacher_user',on_delete=models.CASCADE,null=True)
    teacher_img=models.ImageField(upload_to='teacher_img/',default=None,null=True)
    fname=models.CharField(max_length=30,default=None,null=True)
    lname=models.CharField(max_length=30,default=None,null=True)
    gender=models.CharField(max_length=10,choices=g,default=None,null=True)
    email=models.CharField(max_length=90,default=None,null=True)
    dob=models.DateField(null=True)
    doj=models.DateField(null=True)
    phone_no=models.CharField(max_length=20,default=None)
    address=models.TextField(null=True)
    salary=models.PositiveIntegerField(null=True)
    expr=models.PositiveIntegerField(null=True)

    ug_uni_name = models.CharField(max_length=100, blank=True, null=True)
    ug_degree_name = models.CharField(max_length=100, blank=True, null=True)
    ug_overall_cgpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # PG Details
    pg_uni_name = models.CharField(max_length=100, blank=True, null=True)
    pg_degree_name = models.CharField(max_length=100, blank=True, null=True)
    pg_overall_cgpa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)


    def __str__(self) -> str:
        return f"{self.fname} - {self.lname} - {self.email}"
    

    def save(self, *args, **kwargs):
        # If the email is being changed, update the associated Parent_user's email
        if self.pk:
            original_teacher = Teacher.objects.get(pk=self.pk)
            if original_teacher.email != self.email:
                self.t_user.teacher_user.email = self.email
                self.t_user.teacher_user.save()
        super(Teacher, self).save(*args, **kwargs)



class Teacher_user(models.Model):
    teacher_user=models.OneToOneField(User,on_delete=models.CASCADE,null=True)


class Parent_user(models.Model):
    parent_user=models.OneToOneField(User,on_delete=models.CASCADE,null=True)

class Parent(models.Model):
    p_user=models.OneToOneField('Parent_user',on_delete=models.CASCADE,null=True)
    parent_img=models.ImageField(upload_to='parent_img/',default=None,null=True)
    fname=models.CharField(max_length=30,default=None,null=True)
    lname=models.CharField(max_length=30,default=None,null=True)
    gender=models.CharField(max_length=10,choices=g,default=None,null=True)
    email=models.CharField(max_length=90,default=None,null=True,unique=True)
    phone_no=models.CharField(max_length=20,default=None,null=True)
    address=models.TextField(null=True)
    year=models.PositiveIntegerField(null=True,default=2024)

    def save(self, *args, **kwargs):
        # If the email is being changed, update the associated Parent_user's email
        if self.pk:
            original_parent = Parent.objects.get(pk=self.pk)
            if original_parent.email != self.email:
                self.p_user.parent_user.email = self.email
                self.p_user.parent_user.save()
        super(Parent, self).save(*args, **kwargs)
    

    def __str__(self) -> str:
        return f"{self.fname}  {self.lname}"


class Subject(models.Model):
    sub_name=models.CharField(max_length=50,default=None)
    Medium=[('English','English'),('Gujarati','Gujarati')]
    cls_name=models.ForeignKey('Class',on_delete=models.CASCADE,default='')
    medium_name=models.CharField(max_length=30,choices=Medium,default='English')

    def __str__(self) -> str:
        return f"{self.sub_name}"

class ContactUs(models.Model):
    name=models.CharField(max_length=50)
    email=models.CharField(max_length=100)
    number=models.CharField(max_length=20)
    subject=models.CharField(max_length=50)
    message=models.TextField()

    def __str__(self) -> str:
        return f"{self.name}"
    
class Curriculum(models.Model):
    pdf=models.FileField(upload_to='Curriculum/')
    Medium=[('English','English'),('Gujarati','Gujarati')]
    cls_name=models.ForeignKey('Class',on_delete=models.CASCADE,default='')
    medium_name=models.CharField(max_length=30,choices=Medium,default='English')

    def __str__(self) -> str:
        return f"{self.medium_name} - {self.cls_name}"

class PTM(models.Model):
    topic=models.CharField(max_length=70,default=None,null=True)
    desc=models.TextField()
    ptm_date=models.DateField()
    ptm_time=models.TimeField()
    Medium=[('English','English'),('Gujarati','Gujarati')]
    cls_name=models.ForeignKey('Class',on_delete=models.CASCADE,default='')
    medium_name=models.CharField(max_length=30,choices=Medium,default='English')

    def __str__(self) -> str:
        return f"{self.medium_name} - {self.cls_name}"

class Timetable(models.Model):
    pdf=models.FileField(upload_to='TimeTable/',default=None)
    Medium=[('English','English'),('Gujarati','Gujarati')]
    cls_name=models.ForeignKey('Class',on_delete=models.CASCADE,default='')
    medium_name=models.CharField(max_length=30,choices=Medium,default='English')

class Marks(models.Model): 
    e=[ ('Semester-1', 'Semester-1'), 
        ('Semester-2', 'Semester-2'),] 
    student=models.ForeignKey('Student',on_delete=models.CASCADE) 
    subject=models.ForeignKey('Subject',on_delete=models.CASCADE) 
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True) 
    total_marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True) 
    exam_date = models.DateField() 
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True) 
    exam=models.CharField(max_length=20,choices=e,null=True) 
    grade=models.CharField(max_length=3,choices=[('A+', 'A+'), 
        ('A', 'A'),('B', 'B'),('B+', 'B+'),('C', 'C'),('F', 'F'),],default="B") 
 
    def __str__(self) -> str: 
        return f"{self.student} - {self.exam}"
    
class Teacher_has_class(models.Model): 
    Medium=[('English','English'),('Gujarati','Gujarati')] 
    cls_name=models.ForeignKey('Class',on_delete=models.CASCADE,default=None) 
    medium_name=models.CharField(max_length=30,choices=Medium,default='English') 
    cls_teacher=models.ForeignKey("Teacher",on_delete=models.CASCADE,default=None)

    




