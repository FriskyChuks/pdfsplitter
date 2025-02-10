from django.urls import path

from .views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('upload_payslip/',upload_payslip_view,name='upload_payslip'),
    path('download-payslip/<int:request_year>/<int:request_month>/<int:user_id>/<int:ippis_no>/', 
         download_payslip_view, name='download_payslip'),
    
]