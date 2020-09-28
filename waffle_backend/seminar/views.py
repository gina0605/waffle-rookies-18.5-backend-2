from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from seminar.models import Seminar, UserSeminar
from seminar.serializers import SeminarSerializer


class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated, )

    def create(self, request):
        user = request.user
        if not hasattr(user, 'instructor'):
            return Response({"error": "Only instructors can create seminars"}, status=status.HTTP_403_FORBIDDEN)
        print(user.instructor)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seminar = serializer.save()
        UserSeminar.objects.create(
            user=user,
            seminar=seminar,
            role = 'instructor'
        )
        print("Only response left")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        user = request.user
        seminar = self.get_object()
        if not UserSeminar.objects.filter(user=user, seminar=seminar, role='instructor').exists():
            return Response(
                {"error": "Only instructors of this seminar can change information"},
                status=status.HTTP_403_FORBIDDEN)

        participants = UserSeminar.objects.filter(seminar=seminar, role='participant').count()
        if 'capacity' in request.data and request.data.get('capacity') < participants:
            return Response(
                {"error": "Cannot set capacity less than the number of participants"},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(seminar, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(seminar, serializer.validated_data)
        return Response(serializer.data)
