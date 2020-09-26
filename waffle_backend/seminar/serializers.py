from rest_framework import serializers
from seminar.models import UserSeminar
from django.contrib.auth.models import User

class ParticipantSeminarSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    joined_at = serializers.SerializerMethodField()
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

    def get_name(self, userseminar):
        return userseminar.seminar.name

    def get_joined_at(self, userseminar):
        return userseminar.created_at

    def get_is_active(self, userseminar):
        return userseminar.dropped_at == None


class InstructorSeminarSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    joined_at = serializers.SerializerMethodField()

    class Meta:
        model = UserSeminar
        fields = (
            'id',
            'name',
            'joined_at',
        )

    def get_name(self, userseminar):
        return userseminar.seminar.name

    def get_joined_at(self, userseminar):
        return userseminar.created_at