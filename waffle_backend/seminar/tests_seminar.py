from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
import datetime

from user.models import InstructorProfile, ParticipantProfile
from seminar.models import Seminar, UserSeminar

class PostSeminarTestCase(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            email="part@mail.com",
        )
        self.part_token = 'Token ' + Token.objects.create(user=part).key

        ParticipantProfile.objects.create(
            user=part,
        )

        partinst = User.objects.create_user(
            username="partinst",
            password="password",
            email="partinst@mail.com",
        )
        self.partinst_token = 'Token ' + Token.objects.create(user=partinst).key
        self.partinst_id = partinst.id

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
        self.inst_token = 'Token ' + Token.objects.create(user=inst).key

        InstructorProfile.objects.create(
            user=inst,
        )

        inst2 = User.objects.create_user(
            username="inst2",
            password="password",
            email="inst2@mail.com",
        )
        self.inst2_token = 'Token ' + Token.objects.create(user=inst2).key
        self.inst2_id = inst2.id

        InstructorProfile.objects.create(
            user=inst2,
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
        )

        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            role="instructor",
        )

    def test_post_seminar_unauthorized(self):
        response = self.client.post(         # Unauthorized
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_request_by_noninstructor(self):
        response = self.client.post(         # Not instructor
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.part_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_request_by_already_instructor(self):
        response = self.client.post(         # Already instructing another seminar
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.inst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_incomplete_request(self):
        response = self.client.post(         # Name blank
            '/api/v1/seminar/',
            json.dumps({
                "name": "",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No capacity
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No count
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # No time
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar_wrong_request(self):
        response = self.client.post(         # capacity not number
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": "a",
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # capacity < 0
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": -1,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # count not number
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": "a",
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # count < 0
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": -1,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # time format wrong
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20:10",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(         # online wrong
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20:10",
                "online": "dd"
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Seminar.objects.count(), 1)
        self.assertEqual(UserSeminar.objects.count(), 2)

    def test_post_seminar(self):
        response = self.client.post(         # Correct
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
            }),
            HTTP_AUTHORIZATION=self.partinst_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 9)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["time"], "13:20")
        self.assertTrue(data["online"])
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.partinst_id)
        self.assertEqual(instructor["username"], "partinst")
        self.assertEqual(instructor["email"], "partinst@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertEqual(len(data["participants"]), 0)


        response = self.client.post(         # Correct
            '/api/v1/seminar/',
            json.dumps({
                "name": "seminar2",
                "capacity": 9,
                "count": 4,
                "time": "13:20",
                "online": "F",
            }),
            HTTP_AUTHORIZATION=self.inst2_token,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "seminar2")
        self.assertEqual(data["capacity"], 9)
        self.assertEqual(data["count"], 4)
        self.assertEqual(data["time"], "13:20")
        self.assertFalse(data["online"])
        self.assertEqual(len(data["instructors"]), 1)
        instructor = data["instructors"][0]
        self.assertEqual(instructor["id"], self.inst2_id)
        self.assertEqual(instructor["username"], "inst2")
        self.assertEqual(instructor["email"], "inst2@mail.com")
        self.assertEqual(instructor["first_name"], "")
        self.assertEqual(instructor["last_name"], "")
        self.assertIn("joined_at", instructor)
        self.assertEqual(len(data["participants"]), 0)

        self.assertEqual(Seminar.objects.count(), 3)
        self.assertEqual(UserSeminar.objects.count(), 4)




