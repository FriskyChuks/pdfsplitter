from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

from django.contrib.auth import get_user_model

User = get_user_model()

class UploadedPDF(models.Model):
    payslip_date = models.DateField()  # e.g., 2024
    file = models.FileField(upload_to='uploads')
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['file', 'payslip_date'], name='unique_file_date')
        ]

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        date_obj = datetime.strptime(str(self.payslip_date), "%Y-%m-%d")
        return f"{date_obj.strftime("%b")} {date_obj.year}"
    

class StaffFileDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    page_number = models.PositiveIntegerField()
    pdf_file = models.ForeignKey(UploadedPDF, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'pdf_file')  # Prevent duplicates
        
    def __str__(self):
        return f"{self.user.first_name}-Page: {self.page_number}, Payslip: {self.pdf_file}"


