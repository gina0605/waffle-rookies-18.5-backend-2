from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Prefetch, Count, Q
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
        if user.user_seminars.filter(role='instructor').exists():
            return Response(
                {"error": "The user is an instructor of another seminar"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seminar = serializer.save()
        UserSeminar.objects.create(
            user=user,
            seminar=seminar,
            role='instructor',
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        user = request.user
        seminar = self.get_object()
        if not user.user_seminars.filter(seminar=seminar, role='instructor').exists():
            return Response(
                {"error": "Only instructors of this seminar can change information"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(seminar, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        participants = seminar.user_seminars.filter(role='participant').count()
        if 'capacity' in request.data and serializer.validated_data.get('capacity') < participants:
            return Response(
                {"error": "Cannot set capacity less than the number of participants"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.update(seminar, serializer.validated_data)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        seminar = self.get_object()
        return Response(self.get_serializer(seminar).data)

    def list(self, request):
        param = request.query_params
        name = param.get('name', '')
        data = ''
        cache_key = 'seminar-list'
        if not name:
            data = cache.get(cache_key)
        if not data:
            seminars = self.get_queryset()\
                .filter(name__contains=name)\
                .prefetch_related(
                    Prefetch(
                        'user_seminars',
                        queryset=UserSeminar.objects.filter(role='instructor'),
                        to_attr='userseminar_instructors'
                    )
                ).prefetch_related('userseminar_instructors__user')
            seminars = seminars.annotate(
                participant_count=Count(
                    'user_seminars',
                    filter=Q(user_seminars__role='participant') & Q(user_seminars__dropped_at=None)
                )
            )
            if param.get('order', '') == 'earliest':
                seminars = seminars.order_by('created_at')
            else:
                seminars = seminars.order_by('-created_at')
            data = self.get_serializer(seminars, many=True).data
            if not name:
                cache.set(cache_key, data, timeout=10)
        return Response(data)

    @action(detail=True, methods=['POST', 'DELETE'])
    def user(self, request, pk):
        user = request.user
        seminar = self.get_object()
        if request.method == 'POST':
            return self._attend_seminar(user, seminar, role=request.data.get('role', ''))
        elif request.method == 'DELETE':
            return self._drop_seminar(user, seminar)

    def _attend_seminar(self, user, seminar, role):
        if role not in ('participant', 'instructor'):
            return Response(
                {"error": "Role should be participant or instructor"},
                status=status.HTTP_400_BAD_REQUEST)
        if not hasattr(user, role):
            return Response(
                {"error": "The user is not a {}".format(role)},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            userseminar = UserSeminar.objects.get(user=user, seminar=seminar)
            if userseminar.dropped_at is not None:
                return Response(
                    {"error": "The user have already dropped out from the seminar"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {"error": "The user is already a member of the seminar"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ObjectDoesNotExist:
            pass
        if role == 'participant':
            if not user.participant.accepted:
                return Response(
                    {"error": "The user is not accepted"},
                    status=status.HTTP_403_FORBIDDEN
                )
            participants = seminar.user_seminars.filter(
                role='participant',
                dropped_at=None,
            ).count()
            if participants >= seminar.capacity:
                return Response(
                    {"error": "This seminar is already full"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif role == 'instructor':
            if user.user_seminars.filter(user=user, role='instructor').exists():
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

    def _drop_seminar(self, user, seminar):
        try:
            userseminar = user.user_seminars.get(seminar=seminar)
        except ObjectDoesNotExist:
            return Response()
        if userseminar.dropped_at is not None:
            return Response()
        if userseminar.role == 'instructor':
            return Response(
                {"error": "Instructors cannot drop seminar"},
                status=status.HTTP_403_FORBIDDEN
            )
        userseminar.dropped_at = timezone.now()
        userseminar.save()
        return Response(self.get_serializer(seminar).data)
