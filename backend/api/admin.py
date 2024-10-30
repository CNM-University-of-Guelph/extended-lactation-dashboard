import os
import sqlite3
import tempfile

from django.contrib import admin
from django.http import HttpResponse
from django.conf import settings
from .models import Cow, Lactation, LactationData, MultiparousFeatures, Prediction, PrimiparousFeatures, DatabaseExport

# Register your models here.
admin.site.register(Cow)
admin.site.register(Lactation)
admin.site.register(LactationData)
admin.site.register(MultiparousFeatures)
admin.site.register(PrimiparousFeatures)
admin.site.register(Prediction)

@admin.register(DatabaseExport)
class DatabaseExportAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    actions = ['download_user_database']

    def download_user_database(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one user to export data.", level='error')
            return

        export = queryset.first()
        user = export.user

        # Create a temporary copy of the SQLite database
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        temp_db_file = tempfile.NamedTemporaryFile(delete=False)
        temp_db_path = temp_db_file.name

        # Connect to the original and temporary databases
        conn = sqlite3.connect(db_path)
        temp_conn = sqlite3.connect(temp_db_path)

        # Copy the schema and data to the temporary database
        with conn:
            conn.backup(temp_conn)

        # Filter data to include only the selected user's data
        cursor = temp_conn.cursor()

        # Get the cow IDs owned by the user
        user_cow_ids = Cow.objects.filter(owner=user).values_list('id', flat=True)
        
        # Get the lactation IDs associated with the user's cows
        user_lactation_ids = Lactation.objects.filter(cow__owner=user).values_list('id', flat=True)

        # Delete rows not belonging to the user
        cursor.execute(f"DELETE FROM api_cow WHERE owner_id != ?", (user.id,))
        cursor.execute(f"DELETE FROM api_lactation WHERE cow_id NOT IN ({','.join('?' for _ in user_cow_ids)})", user_cow_ids)
        cursor.execute(f"DELETE FROM api_lactationdata WHERE lactation_id NOT IN ({','.join('?' for _ in user_lactation_ids)})", user_lactation_ids)
        cursor.execute(f"DELETE FROM api_multiparousfeatures WHERE lactation_id NOT IN ({','.join('?' for _ in user_lactation_ids)})", user_lactation_ids)
        cursor.execute(f"DELETE FROM api_primiparousfeatures WHERE lactation_id NOT IN ({','.join('?' for _ in user_lactation_ids)})", user_lactation_ids)
        cursor.execute(f"DELETE FROM api_prediction WHERE lactation_id NOT IN ({','.join('?' for _ in user_lactation_ids)})", user_lactation_ids)

        temp_conn.commit()
        temp_conn.close()

        # Serve the temporary SQLite file as a downloadable file
        with open(temp_db_path, 'rb') as db_file:
            response = HttpResponse(db_file, content_type='application/x-sqlite3')
            response['Content-Disposition'] = f'attachment; filename="user_{user.id}_db.sqlite3"'
            return response

    download_user_database.short_description = 'Download User-Specific Database'
    