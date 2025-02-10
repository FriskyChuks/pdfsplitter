from django.contrib.auth.models import AbstractUser
from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()


class UserGroup(models.Model):
    group = models.CharField(max_length=50)

    def __str__(self):
        return self.group
    
    class Meta:
        db_table = 'accounts_usergroup'  # Use the exact table name from the old database


class Gender(models.Model):
    title = models.CharField(blank=True, null=True, max_length=10)

    def __str__(self):
        return self.title    
    
    class Meta:
        db_table = 'accounts_gender'  # Use the exact table name from the old database


class GradeLevel(models.Model):
    level = models.IntegerField()

    def __str__(self):
        return str(self.level)
    
    class Meta:
        db_table = 'registry_gradelevel'  # Use the exact table name from the old database


class SalaryScale(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'registry_salaryscale'  # Use the exact table name from the old database


class Directorate(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'accounts_directorate'  # Use the exact table name from the old database


class Department(models.Model):
    title = models.CharField(max_length=50, unique=True)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE)
    has_unit = models.BooleanField(default=True)
    reports_to_cmd = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'accounts_department'  # Use the exact table name from the old database


class Unit(models.Model):
    title = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'accounts_unit'  # Use the exact table name from the old database



class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    other_name = models.CharField(blank=True, null=True, max_length=50)
    file_number = models.IntegerField(unique=True, blank=True, null=True)
    username = models.CharField(unique=True, max_length=30)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True)
    user_group = models.ForeignKey(
        UserGroup, on_delete=models.CASCADE, blank=True, null=True)
    passport = models.ImageField(
        upload_to='passport', null=True, blank=True, default="default.jpg")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'other_name', 'file_number',
                       'date_of_birth', 'gender', 'directorate', 'department')
    
    class Meta:
        db_table = 'accounts_user'  # Use the exact table name from the old database

    def __str__(self):
        return str(self.username)

    @property
    def imageURL(self):
        try:
            url = self.passport.url
        except:
            url = ''
        return url


class StaffCategory(models.Model):
    title = models.CharField(max_length=6)

    def __str__(self):
        return self.title


class EmploymentDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ministry = models.CharField(max_length=100)
    designation = models.CharField(max_length=50, null=True, blank=True)
    salary_scale = models.ForeignKey(SalaryScale, on_delete=models.CASCADE)
    staff_category = models.ForeignKey(
        StaffCategory, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.ForeignKey(
        GradeLevel, on_delete=models.CASCADE, null=True, blank=True)
    step = models.IntegerField(null=True, blank=True)
    ippis_no = models.IntegerField(null=True, blank=True)
    qualifications = models.CharField(max_length=225, blank=True, null=True)
    rank = models.CharField(max_length=225, blank=True, null=True)
    first_appointment_date = models.DateField(blank=True, null=True)
    confirmation_date = models.DateField(blank=True, null=True)
    date_of_appt_with_fmc = models.DateField(blank=True, null=True)
    present_appt_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.user)
    
    class Meta:
        db_table = 'registry_employmentdetails'  # Use the exact table name from the old database