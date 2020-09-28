from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from seminar.models import Seminar, UserSeminar
from seminar.serializers import SeminarSerializer


class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        return super(SeminarViewSet, self).get_permissions()

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
