from django.shortcuts import render,redirect
import fitz  # PyMuPDF
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import os
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import io
from django.core.cache import cache

from django.contrib.auth import get_user_model
User = get_user_model()

from accounts.models import EmploymentDetails

from .models import *
from .tasks import process_pdf_task

@login_required
def upload_payslip_view(request):
    users_dict = EmploymentDetails.objects.values_list('user__id', 'ippis_no')
    users_dict = dict(users_dict)

    pdf_files = UploadedPDF.objects.all().order_by('date_uploaded')
    for file in pdf_files:
        file.display_name = os.path.basename(file.file.name)

    if request.method == 'POST':
        get_file = request.FILES['payslip']
        payslip_date_str = request.POST.get('payslip_date')

        try:
            payslip_date = datetime.strptime(payslip_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('upload_payslip')

        existing_file = UploadedPDF.objects.filter(
            payslip_date__year=payslip_date.year,
            payslip_date__month=payslip_date.month
        ).exists()

        if existing_file:
            messages.error(request, f'A file for {payslip_date.strftime("%B %Y")} already exists, check before trying again.')
            return redirect('upload_payslip')

        original_file_name = os.path.basename(get_file.name)
        save_path = os.path.join('pdfs', original_file_name)

        file_instance = UploadedPDF(payslip_date=payslip_date)
        file_instance.file.save(save_path, ContentFile(get_file.read()), save=False)
        file_instance.save()

        print(f"Saved file: {file_instance.file.name}")

        # initiates celery task
        process_pdf_task.delay(file_instance.id, users_dict)
        print("Task initiated.")

        messages.success(request, 'Upload successful; \nThe file is being processed at the background')
        return redirect('home')

    return render(request, 'main/upload_payslip.html', {"pdf_files": pdf_files})



def home_view(request):
    ippis_no, ippis_staff = None, None
    if not request.user.is_authenticated:
        if request.method == 'POST':
            messages.info(request, "You must be logged in to print/download your payslip.")
            return redirect('home')
    else:
        user = request.user
        ippis_staff = user.user_group.group == 'ippis'
        if ippis_staff:
            ippis_no = request.POST.get('ippis_no')
        else:
            try:
                ippis_no = EmploymentDetails.objects.get(user_id=user.id).ippis_no
            except ObjectDoesNotExist:
                messages.info('User has no matching IPPIS Number')
                return redirect('home')

        if request.method == 'POST':
            payslip_date = request.POST.get('payslip_date')

            try:
                user = EmploymentDetails.objects.get(ippis_no=ippis_no).user
            except EmploymentDetails.DoesNotExist:
                messages.error(request, "Your employment details could not be found.")
                return redirect('home')

            if not payslip_date:
                messages.error(request, "No date was provided. Please select a valid date.")
                return redirect('home')

            try:
                # Parse the date and extract month and year
                date_obj = datetime.strptime(payslip_date, "%Y-%m-%d")
                month = date_obj.month
                year = date_obj.year

                # Redirect to the download view with the required parameters
                return redirect('download_payslip', request_year=year, request_month=month, user_id=user.id, ippis_no=ippis_no)
            except ValueError:
                messages.error(request, "Invalid date format. Please select a valid date.")
                return redirect('home')

    return render(request, 'error_pages/unavailable.html', {"ippis_no":ippis_no, "ippis_staff":ippis_staff})
    # return render(request, 'main/index.html', {"ippis_no":ippis_no, "ippis_staff":ippis_staff})



@login_required
def download_payslip_view(request, request_year, request_month, user_id, ippis_no):
    try:
        # Fetch the payslip details
        payslip_detail = get_object_or_404(
            StaffFileDetail,
            user_id=user_id,
            pdf_file__payslip_date__month=request_month,
            pdf_file__payslip_date__year=request_year
        )

        # Ensure the file exists
        pdf_path = str(payslip_detail.pdf_file.file.path)  # Ensure pdf_path is a string
        if not os.path.isfile(pdf_path):
            messages.error(request, "The requested file does not exist on the server.")
            return render(request, 'main/index.html', {})

        # Extract the specific page
        with fitz.open(pdf_path) as pdf:
            if payslip_detail.page_number >= len(pdf):
                messages.error(request, "The specified page does not exist in the PDF.")
                return render(request, 'main/index.html', {})

            # Create a new PDF for the extracted page
            pdf_writer = fitz.open()
            pdf_writer.insert_pdf(pdf, from_page=payslip_detail.page_number, to_page=payslip_detail.page_number)

            # Save the new PDF to an in-memory buffer
            buffer = io.BytesIO()
            pdf_writer.save(buffer, garbage=4, deflate=True)
            buffer.seek(0)  # Reset buffer pointer to the beginning

            # Prepare the HTTP response
            response = HttpResponse(buffer, content_type='application/pdf')
            filename = f"Payslip_{payslip_detail.pdf_file.payslip_date.strftime('%b_%Y')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    except Exception as e:
        # Log and display the error
        messages.error(request, f"Error processing the request: No record matches the given number {ippis_no}")
        # messages.error(request, f"An error occurred while processing the request: {str(e)}")
        return redirect('home')

    return render(request, 'main/index.html', {})
