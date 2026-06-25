from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
import random
from .models import EmergencyRequest
from .serializers import EmergencyRequestSerializer
from doctors.models import Doctor

class EmergencyRequestListCreateView(generics.ListCreateAPIView):
    """
    API view to register an emergency dispatch or fetch active emergency records.
    """
    serializer_class = EmergencyRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return EmergencyRequest.objects.filter(patient__user=user).order_by('-created_at')
        elif user.role in ['DOCTOR', 'ADMIN']:
            return EmergencyRequest.objects.all().order_by('-created_at')
        return EmergencyRequest.objects.none()

    def perform_create(self, serializer):
        serializer.save()

class NearbyFacilitiesView(APIView):
    """
    Returns mock locations of nearby hospitals, clinics, and doctors 
    calculated using offsets relative to the user's current GPS location.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params.get('latitude'))
            lng = float(request.query_params.get('longitude'))
        except (TypeError, ValueError):
            return Response(
                {"error": "Valid latitude and longitude query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate 3 hospitals with random offsets
        hospitals = [
            {
                "id": 1,
                "name": "City General Hospital (Emergency Center)",
                "type": "HOSPITAL",
                "latitude": lat + 0.0045,
                "longitude": lng - 0.0031,
                "phone": "+1 (555) 911-0111"
            },
            {
                "id": 2,
                "name": "St. Jude Medical Center",
                "type": "HOSPITAL",
                "latitude": lat - 0.0072,
                "longitude": lng + 0.0051,
                "phone": "+1 (555) 911-0222"
            },
            {
                "id": 3,
                "name": "Mercy Urgent Care",
                "type": "HOSPITAL",
                "latitude": lat + 0.0021,
                "longitude": lng + 0.0089,
                "phone": "+1 (555) 911-0333"
            }
        ]

        # Generate 2 clinics with random offsets
        clinics = [
            {
                "id": 1,
                "name": "MediKal Family Clinic",
                "type": "CLINIC",
                "latitude": lat - 0.0035,
                "longitude": lng - 0.0062,
                "phone": "+1 (555) 234-5678"
            },
            {
                "id": 2,
                "name": "Apex Pediatric & General Care",
                "type": "CLINIC",
                "latitude": lat + 0.0081,
                "longitude": lng - 0.0022,
                "phone": "+1 (555) 876-5432"
            }
        ]

        # Fetch actual online doctors from the database and add minor mock location offsets
        nearby_doctors = []
        online_doctors = Doctor.objects.filter(online_status=True, verification_status='APPROVED')[:3]
        
        # Fallback doctors if database seeding hasn't run yet
        fallback_docs = [
            {"id": 101, "name": "Dr. Sarah Jenkins", "specialization": "General Physician", "lat_off": -0.002, "lng_off": 0.003},
            {"id": 102, "name": "Dr. James Carter", "specialization": "Cardiologist", "lat_off": 0.005, "lng_off": -0.004}
        ]

        if online_doctors.exists():
            for idx, doc in enumerate(online_doctors):
                # Minor offsets (+/- 0.01)
                lat_off = 0.003 if idx % 2 == 0 else -0.004
                lng_off = -0.005 if idx % 2 == 0 else 0.006
                nearby_doctors.append({
                    "id": doc.id,
                    "name": f"Dr. {doc.user.full_name}",
                    "specialization": doc.specialization,
                    "type": "DOCTOR",
                    "latitude": lat + lat_off,
                    "longitude": lng + lng_off,
                    "phone": doc.user.phone or "+1 (555) 000-1111"
                })
        else:
            for doc in fallback_docs:
                nearby_doctors.append({
                    "id": doc["id"],
                    "name": doc["name"],
                    "specialization": doc["specialization"],
                    "type": "DOCTOR",
                    "latitude": lat + doc["lat_off"],
                    "longitude": lng + doc["lng_off"],
                    "phone": "+1 (555) 000-1111"
                })

        return Response({
            "hospitals": hospitals,
            "clinics": clinics,
            "doctors": nearby_doctors
        }, status=status.HTTP_200_OK)
