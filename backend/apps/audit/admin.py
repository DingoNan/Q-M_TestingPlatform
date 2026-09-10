from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'action', 'method', 'path', 'module',
                    'status_code', 'description', 'create_time')
    list_filter = ('action', 'method', 'module', 'status_code')
    search_fields = ('username', 'path', 'description')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    ordering = ['-create_time']
