from django.contrib import admin
from .models import Prescription, MedicineOrder

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('patient__user__full_name', 'doctor__user__full_name')

@admin.register(MedicineOrder)
class MedicineOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user__full_name', 'delivery_address')
    list_editable = ('status', 'total_price')
