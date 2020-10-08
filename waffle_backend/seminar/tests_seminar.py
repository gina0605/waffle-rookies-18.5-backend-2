from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
import datetime

from user.models import InstructorProfile, ParticipantProfile
from seminar.models import Seminar, UserSeminar

class PostSeminar(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_token = 'Token ' + Token.objects.create(user=part)

        ParticipantProfile.objects.create(
            user=part,
        )

        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'Token ' + Token.objects.create(user=partinst)

        ParticipantProfile.objects.create(
            user=partinst,
        )

        InstructorProfile.objects.create(
            user=partinst,
        )

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'Token ' + Token.objects.create(user=inst)

        InstructorProfile.objects.create(
            user=inst,
        )

        seminar = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=datetime.time(hour=14, minute=30),
        )

        UserSeminar.objects.create(
            user=partinst,
            seminar=seminar,
            role="participant",
            dropped_at=None,
        )

        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            role="instructor",
            dropped_at=None,
        )

    def post_seminar_unauthorized(self):
        response = self.client.get(         # Unauthorized
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": datetime.time(hour=13, minute=20),
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
