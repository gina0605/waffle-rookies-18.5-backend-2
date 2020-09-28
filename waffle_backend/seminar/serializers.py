from rest_framework import serializers
from seminar.models import Seminar, UserSeminar


class SeminarSerializer(serializers.ModelSerializer):
    instructors = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Seminar
        fields = (
            'id',
            'name',
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
    joined_at = serializers.DateTimeField(source='created_at')

    class Meta:
        model = UserSeminar
        fields = (
            'id',
            'joined_at',
        )


class SeminarParticipantSerializer(serializers.ModelSerializer):
    joined_at = serializers.DateTimeField(source='created_at')

    class Meta:
        model = UserSeminar
        fields = (
            'joined_at',
        )
