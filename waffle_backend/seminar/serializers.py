from rest_framework import serializers
from seminar.models import Seminar, UserSeminar


class SeminarSerializer(serializers.ModelSerializer):
    instructors = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    online = serializers.BooleanField(default=True)

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'description',
            'capacity',
            'count',
            'time',
            'start_date',
            'online',
            'instructors',
            'participants',
        )

    def get_instructors(self, seminar):
        queryset = UserSeminar.objects.filter(seminar=seminar, role='instructor')
        return SeminarInstructorSerializer(queryset, many=True).data

    def get_participants(self, seminar):
        queryset = UserSeminar.objects.filter(seminar=seminar, role='participant')
        return SeminarParticipantSerializer(queryset, many=True).data


class SimpleSeminarSerializer(serializers.ModelSerializer):
    instructors = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
            'description',
            'instructors',
            'participant_count'
        )

    def get_instructors(self, seminar):
        queryset = UserSeminar.objects.filter(seminar=seminar, role='instructor')
        return SeminarInstructorSerializer(queryset, many=True).data

    def get_participant_count(self, seminar):
        return UserSeminar.objects.filter(
            seminar=seminar,
            role='participant',
            dropped_at=None,
        ).count()


class ParticipantSeminarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='seminar.name')
    joined_at = serializers.DateTimeField(source='created_at')
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSeminar
        fields = (
            'id',
            'name',
            'joined_at',
            'is_active',
            'dropped_at',
        )

    def get_is_active(self, userseminar):
        return userseminar.dropped_at == None


class InstructorSeminarSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='seminar.id')
    name = serializers.CharField(source='seminar.name')
    joined_at = serializers.DateTimeField(source='created_at')

    class Meta:
        model = UserSeminar
        fields = (
            'id',
            'name',
            'joined_at',
        )


class SeminarInstructorSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    joined_at = serializers.DateTimeField(source='created_at')

    class Meta:
        model = UserSeminar
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_at',
        )


class SeminarParticipantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    joined_at = serializers.DateTimeField(source='created_at')
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = UserSeminar
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'joined_at',
            'is_active',
            'dropped_at',
        )

    def get_is_active(self, userseminar):
        return userseminar.dropped_at is None
