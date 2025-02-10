# tasks.py
from celery import shared_task
from .models import UploadedPDF, StaffFileDetail
from django.db import IntegrityError
import fitz
import re
import os

@shared_task
def process_pdf_task(file_id, users_dict):
    print("Starting celery task: pdf splitting in process")
    try:
        file_instance = UploadedPDF.objects.get(id=file_id)
        file_path = os.path.abspath(file_instance.file.path)
        # print(f"Processing file at: {file_path}")

        with fitz.open(file_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                text = page.get_text()
                print(f"Page {page_num} text: {text[:100]}...")  # Print the first 100 characters

                for user_id, ippis_no in users_dict.items():
                    pattern = r'\b' + re.escape(str(ippis_no)) + r'\b'
                    # print(f"Searching for pattern: {pattern} in text")

                    if re.search(pattern, text):
                        try:
                            staff_file, created = StaffFileDetail.objects.get_or_create(
                                user_id=user_id,
                                page_number=page_num,
                                pdf_file_id=file_instance.id
                            )
                            # if created:
                            #     print(f"Created record for user_id: {user_id}, page_number: {page_num}, file_id: {file_instance.id}")
                            # else:
                            #     print(f"Record already exists for user_id: {user_id}, page_number: {page_num}, file_id: {file_instance.id}")
                        except IntegrityError as e:
                            pass
                            # print(f"IntegrityError while processing user_id: {user_id}, page_number: {page_num}, file_id: {file_instance.id}. Error: {e}")

        print("Task Completed: Staff can access their payslips now")
        return "Task Completed"

    except Exception as e:
        print(f"Error processing file_id: {file_id}. Error: {e}")
        return f"Error: {e}"
