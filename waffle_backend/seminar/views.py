from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from seminar.models import Seminar, UserSeminar
from seminar.serializers import SeminarSerializer, SimpleSeminarSerializer


class SeminarViewSet(viewsets.GenericViewSet):
    queryset = Seminar.objects.all()
    serializer_class = SeminarSerializer
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        if self.action in ('retrieve', 'list'):
            return (AllowAny(), )
        else:
            return super(SeminarViewSet, self).get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleSeminarSerializer
        return self.serializer_class

    def create(self, request):
        user = request.user
        if not hasattr(user, 'instructor'):
            return Response(
                {"error": "Only instructors can create seminars"},
                status=status.HTTP_403_FORBIDDEN
            )
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
                status=status.HTTP_403_FORBIDDEN
            )

        participants = UserSeminar.objects.filter(seminar=seminar, role='participant').count()
        if 'capacity' in request.data and request.data.get('capacity') < participants:
            return Response(
                {"error": "Cannot set capacity less than the number of participants"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(seminar, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(seminar, serializer.validated_data)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        seminar = self.get_object()
        return Response(self.get_serializer(seminar).data)

    def list(self, request):
        param = request.query_params
        name = param.get('name', '')
        seminars = self.get_queryset().filter(name__contains=name)
        if param.get('order', '') == 'earliest':
            seminars.order_by('created_at')
        return Response(self.get_serializer(seminars, many=True).data)

    @action(detail=True, methods=['POST'])
    def user(self, request, pk):
        user = request.user
        seminar = self.get_object()
        role = request.data.get('role', '')
        if role not in ('participant', 'instructor'):
            return Response(
                {"error": "Role should be participant or instructor"},
                status=status.HTTP_400_BAD_REQUEST)
        if not hasattr(user, role):
            return Response(
                {"error": "The user is not a {}".format(role)},
                status=status.HTTP_403_FORBIDDEN
            )
        if UserSeminar.objects.filter(user=user, seminar=seminar).exists():
            return Response(
                {"error": "The user is already a member of the seminar"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if role == 'participant':
            if not user.participant.accepted:
                return Response(
                    {"error": "The user is not accepted"},
                    status=status.HTTP_403_FORBIDDEN
                )
            participants = UserSeminar.objects.filter(seminar=seminar, role='participant').count()
            if participants == seminar.capacity:
                return Response(
                    {"error": "This seminar is already full"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif role == 'instructor':
            if UserSeminar.objects.filter(user=user, role='instructor').exists():
                return Response(
                    {"error": "The user is an instructor of another seminar"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        UserSeminar.objects.create(
            user=user,
            seminar=seminar,
            role=role,
        )
        return Response(self.get_serializer(seminar).data, status=status.HTTP_201_CREATED)
