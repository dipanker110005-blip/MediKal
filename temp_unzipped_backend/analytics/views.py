from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from appointments.models import Appointment
from patients.models import Patient
from doctors.models import Doctor

from accounts.permissions import IsAdmin, IsDoctor

class AdminAnalyticsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        completed_appointments = Appointment.objects.filter(status='COMPLETED')
        total_revenue = completed_appointments.aggregate(Sum('total_fee'))['total_fee__sum'] or 0.00
        
        patient_count = Patient.objects.count()
        doctor_count = Doctor.objects.count()
        appointment_count = Appointment.objects.count()

        # Status breakdown
        status_breakdown = {
            'PENDING': Appointment.objects.filter(status='PENDING').count(),
            'CONFIRMED': Appointment.objects.filter(status='CONFIRMED').count(),
            'COMPLETED': Appointment.objects.filter(status='COMPLETED').count(),
            'CANCELLED': Appointment.objects.filter(status='CANCELLED').count(),
        }

        # Revenue timeline (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        daily_revenue = (
            Appointment.objects.filter(status='COMPLETED', date__range=[start_date, end_date])
            .values('date')
            .annotate(revenue=Sum('total_fee'))
            .order_by('date')
        )
        revenue_dict = {item['date']: item['revenue'] for item in daily_revenue}
        
        revenue_timeline = []
        current_date = start_date
        while current_date <= end_date:
            revenue_timeline.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "revenue": float(revenue_dict.get(current_date) or 0.00)
            })
            current_date += timedelta(days=1)

        # Specialty breakdown (based on appointments)
        specialty_data = (
            Appointment.objects.values('doctor__specialization')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        specialty_breakdown = {item['doctor__specialization']: item['count'] for item in specialty_data if item['doctor__specialization']}

        # Consultation Type breakdown
        type_data = (
            Appointment.objects.values('consultation_type')
            .annotate(count=Count('id'))
        )
        type_breakdown = {item['consultation_type']: item['count'] for item in type_data}

        # Patient Age Demographics
        patients = Patient.objects.all()
        age_demographics = {
            'Under 18': 0,
            '18-35': 0,
            '36-50': 0,
            '50+': 0,
            'Unknown': 0
        }
        for p in patients:
            if p.age is None:
                age_demographics['Unknown'] += 1
            elif p.age < 18:
                age_demographics['Under 18'] += 1
            elif p.age <= 35:
                age_demographics['18-35'] += 1
            elif p.age <= 50:
                age_demographics['36-50'] += 1
            else:
                age_demographics['50+'] += 1

        # Patient Blood Group breakdown
        blood_data = (
            Patient.objects.values('blood_group')
            .annotate(count=Count('id'))
        )
        blood_group_breakdown = {item['blood_group'] or 'Unknown': item['count'] for item in blood_data}

        return Response({
            'total_revenue': float(total_revenue),
            'patient_count': patient_count,
            'doctor_count': doctor_count,
            'appointment_count': appointment_count,
            'status_breakdown': status_breakdown,
            'revenue_timeline': revenue_timeline,
            'specialty_breakdown': specialty_breakdown,
            'type_breakdown': type_breakdown,
            'age_demographics': age_demographics,
            'blood_group_breakdown': blood_group_breakdown
        }, status=status.HTTP_200_OK)


class DoctorAnalyticsView(APIView):
    permission_classes = [IsDoctor | IsAdmin]

    def get(self, request):
        is_doctor = request.user.role == 'DOCTOR'
        is_admin = request.user.role == 'ADMIN' or request.user.is_staff
        
        # Retrieve Doctor profile
        if is_doctor:
            try:
                doctor = Doctor.objects.get(user=request.user)
            except Doctor.DoesNotExist:
                return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # If admin, fetch the doctor specified in query parameters, else return 400
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({"detail": "doctor_id query parameter required for administrators."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                doctor = Doctor.objects.get(id=doctor_id)
            except Doctor.DoesNotExist:
                return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)

        doctor_appointments = Appointment.objects.filter(doctor=doctor)
        completed_appointments = doctor_appointments.filter(status='COMPLETED')
        
        total_consultations = completed_appointments.count()
        total_earnings = completed_appointments.aggregate(Sum('total_fee'))['total_fee__sum'] or 0.00
        
        # Unique patients seen
        patient_count = doctor_appointments.values('patient').distinct().count()

        # Status breakdown
        status_breakdown = {
            'PENDING': doctor_appointments.filter(status='PENDING').count(),
            'CONFIRMED': doctor_appointments.filter(status='CONFIRMED').count(),
            'COMPLETED': doctor_appointments.filter(status='COMPLETED').count(),
            'CANCELLED': doctor_appointments.filter(status='CANCELLED').count(),
        }

        # Consultation Type breakdown
        type_data = (
            doctor_appointments.values('consultation_type')
            .annotate(count=Count('id'))
        )
        type_breakdown = {item['consultation_type']: item['count'] for item in type_data}

        # Earnings timeline (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)
        daily_earnings = (
            completed_appointments.filter(date__range=[start_date, end_date])
            .values('date')
            .annotate(earnings=Sum('total_fee'))
            .order_by('date')
        )
        earnings_dict = {item['date']: item['earnings'] for item in daily_earnings}
        
        earnings_timeline = []
        current_date = start_date
        while current_date <= end_date:
            earnings_timeline.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "earnings": float(earnings_dict.get(current_date) or 0.00)
            })
            current_date += timedelta(days=1)

        return Response({
            'total_consultations': total_consultations,
            'total_earnings': float(total_earnings),
            'patient_count': patient_count,
            'rating': float(doctor.rating),
            'status_breakdown': status_breakdown,
            'type_breakdown': type_breakdown,
            'earnings_timeline': earnings_timeline
        }, status=status.HTTP_200_OK)
