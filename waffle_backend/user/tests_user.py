from django.contrib.auth.models import User
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
import json
import datetime

from user.models import InstructorProfile, ParticipantProfile
from seminar.models import Seminar, UserSeminar


class PostUserTestCase(TestCase):
    client = Client()

    def setUp(self):
        user1 = User.objects.create_user(
            username="user1",
            password="password",
            email="user1@mail.com",
            first_name="Kildong",
            last_name="Hong",
        )
        ParticipantProfile.objects.create(
            user=user1,
            university="university1",
            accepted=True,
        )

    def test_post_user_duplicated_username(self):
        response = self.client.post(        # Same username
            '/api/v1/user/',
            json.dumps({
                "username": "user1",
                "password": "password",
                "first_name": "CS",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user_incomplete_request(self):
        response = self.client.post(        # No username
            '/api/v1/user/',
            json.dumps({
                "password": "password",
                "first_name": "CS",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(        # No password
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "first_name": "CS",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(        # Wrong role
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "password": "password",
                "first_name": "CS",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "wrong_role",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(        # No role
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "password": "password",
                "first_name": "CS",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(        # No email
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "password": "password",
                "first_name": "CS",
                "last_name": "Kim",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user_wrong_request(self):
        response = self.client.post(        # Only first_name, no last_name
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "password": "password",
                "first_name": "CS",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(        # Only last_name, first_name blank
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "password": "password",
                "first_name": "",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(        # Number in first_name
            '/api/v1/user/',
            json.dumps({
                "username": "user2",
                "password": "password",
                "first_name": "CS0",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

    def test_post_user(self):
        response = self.client.post(        # Same username
            '/api/v1/user/',
            json.dumps({
                "username": "user1",
                "password": "password",
                "first_name": "CS",
                "last_name": "Kim",
                "email": "kcs@mail.com",
                "role": "participant",
                "university": "university1"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_count = User.objects.count()
        self.assertEqual(user_count, 1)

        response = self.client.post(        # Correct, first_name and last_name both exist
            '/api/v1/user/',
            json.dumps({
                "username": "participant",
                "password": "password",
                "first_name": "Davin",
                "last_name": "Byeon",
                "email": "bdv111@snu.ac.kr",
                "role": "participant",
                "university": "university2"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "participant")
        self.assertEqual(data["email"], "bdv111@snu.ac.kr")
        self.assertEqual(data["first_name"], "Davin")
        self.assertEqual(data["last_name"], "Byeon")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertIn("token", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["university"], "university2")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 0)

        self.assertIsNone(data["instructor"])

        response = self.client.post(        # Correct, first_name and last_name both not exist
            '/api/v1/user/',
            json.dumps({
                "username": "instructor",
                "password": "password",
                "email": "bdv111@snu.ac.kr",
                "role": "instructor",
                "university": "university2",
                "company": "company"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "instructor")
        self.assertEqual(data["email"], "bdv111@snu.ac.kr")
        self.assertEqual(data["first_name"], "")
        self.assertEqual(data["last_name"], "")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertIn("token", data)

        self.assertIsNone(data["participant"])

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertEqual(instructor["company"], "company")
        self.assertIsNone(instructor["year"])
        self.assertIsNone(instructor["charge"])


        user_count = User.objects.count()
        self.assertEqual(user_count, 3)
        participant_count = ParticipantProfile.objects.count()
        self.assertEqual(participant_count, 2)
        instructor_count = InstructorProfile.objects.count()
        self.assertEqual(instructor_count, 1)


class PutUserLoginTestCase(TestCase):
    client = Client()

    def setUp(self):
        user1 = User.objects.create_user(
            username="user1",
            password="password",
            email="user1@mail.com",
        )
        ParticipantProfile.objects.create(
            user=user1,
        )

    def test_put_user_login_incomplete_request(self):
        response = self.client.post(        # No username
            '/api/v1/user/login/',
            json.dumps({
                "password": "password",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(        # No password
            '/api/v1/user/login/',
            json.dumps({
                "username": "user1",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_login_wrong_request(self):
        response = self.client.post(        # Wrong username
            '/api/v1/user/login/',
            json.dumps({
                "username": "username_wrong",
                "password": "password"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(        # Wrong password
            '/api/v1/user/login/',
            json.dumps({
                "username": "user1",
                "password": "password_wrong"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_user_login(self):
        response = self.client.put(        # Correct
            '/api/v1/user/login/',
            json.dumps({
                "username": "user1",
                "password": "password",
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "user1")
        self.assertEqual(data["email"], "user1@mail.com")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertIn("token", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["accepted"], True)
        self.assertEqual(len(participant["seminars"]), 0)

        self.assertIsNone(data["instructor"])


class PutUserMeTestCase(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            email="part@mail.com",
            first_name="Kildong",
            last_name="Hong",
        )
        ParticipantProfile.objects.create(
            user=part,
            university="university1",
        )
        self.participant_token = 'Token ' + Token.objects.create(user=part).key

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        InstructorProfile.objects.create(
            user=inst,
            year=1,
        )
        self.instructor_token = 'Token ' + Token.objects.create(user=inst).key

    def test_put_user_unauthorized_request(self):
        response = self.client.put(         # Unauthorized
            '/api/v1/user/me/',
            json.dumps({
                "email": "Part@mail.com"
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        participant_user = User.objects.get(username='part')
        self.assertEqual(participant_user.email, "part@mail.com")

    def test_put_user_wrong_request(self):
        response = self.client.put(         # Only first_name, no last_name
            '/api/v1/user/me/',
            json.dumps({
                "first_name": "Kildong",
                "email": "Part@mail.com"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        participant_user = User.objects.get(username='part')
        self.assertEqual(participant_user.first_name, 'Kildong')
        self.assertEqual(participant_user.last_name, 'Hong')
        self.assertEqual(participant_user.email, 'part@mail.com')

        response = self.client.put(         # Only last_name, first_name blank
            '/api/v1/user/me/',
            json.dumps({
                "first_name": "",
                "last_name": "Kim",
                "email": "Part@mail.com"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        participant_user = User.objects.get(username='part')
        self.assertEqual(participant_user.first_name, 'Kildong')
        self.assertEqual(participant_user.last_name, 'Hong')
        self.assertEqual(participant_user.email, 'part@mail.com')

        response = self.client.put(         # Number in last_name
            '/api/v1/user/me/',
            json.dumps({
                "first_name": "CS0",
                "last_name": "Kim",
                "university": "university2",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        participant_user = User.objects.get(username='part')
        self.assertEqual(participant_user.first_name, 'Kildong')
        self.assertEqual(participant_user.last_name, 'Hong')
        self.assertEqual(participant_user.participant.university, 'university1')

        response = self.client.put(         # Year < 0
            '/api/v1/user/me/',
            json.dumps({
                "username": "Inst",
                "email": "Inst@mail.com",
                "company": "company",
                "year": -1
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        instructor_user = User.objects.get(username='inst')
        self.assertEqual(instructor_user.email, 'inst@mail.com')
        instructor = instructor_user.instructor
        self.assertEqual(instructor.company, "")
        self.assertEqual(instructor.year, 1)

        response = self.client.put(         # Year not number
            '/api/v1/user/me/',
            json.dumps({
                "username": "Inst",
                "email": "Inst@mail.com",
                "year": "a"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        instructor_user = User.objects.get(username='inst')
        self.assertEqual(instructor_user.email, 'inst@mail.com')
        self.assertEqual(instructor_user.instructor.year, 1)

    def test_put_user_me_participant(self):
        response = self.client.put(         # Correct
            '/api/v1/user/me/',
            json.dumps({
                "username": "Part",
                "email": "Part@mail.com",
                "university": "university2",
                "accepted": "F",
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.participant_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "Part")
        self.assertEqual(data["email"], "Part@mail.com")
        self.assertEqual(data["first_name"], "Kildong")
        self.assertEqual(data["last_name"], "Hong")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertNotIn("token", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertIn("id", participant)
        self.assertEqual(participant["university"], "university2")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 0)

        self.assertIsNone(data["instructor"])

        participant_user = User.objects.get(username='Part')
        self.assertEqual(participant_user.email, 'Part@mail.com')
        self.assertEqual(participant_user.participant.university, 'university2')
        self.assertTrue(participant_user.participant.accepted)
        self.assertFalse(hasattr(participant_user, 'instructor'))

    def test_put_user_me_instructor(self):
        response = self.client.put(
            '/api/v1/user/me/',
            json.dumps({
                "username": "Inst",
                "email": "Inst@mail.com",
                "first_name": "CS",
                "last_name": "Kim",
                "university": "university1",  # this should be ignored
                "company": "company1",
                "year": 0
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.instructor_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "Inst")
        self.assertEqual(data["email"], "Inst@mail.com")
        self.assertEqual(data["first_name"], "CS")
        self.assertEqual(data["last_name"], "Kim")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertNotIn("token", data)

        self.assertIsNone(data["participant"])

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertIn("id", instructor)
        self.assertEqual(instructor["company"], "company1")
        self.assertEqual(instructor["year"], 0)
        self.assertIsNone(instructor["charge"])

        instructor_user = User.objects.get(username='Inst')
        self.assertEqual(instructor_user.email, 'Inst@mail.com')
        self.assertEqual(instructor_user.first_name, 'CS')
        self.assertEqual(instructor_user.last_name, 'Kim')
        self.assertFalse(hasattr(instructor_user, 'participant'))
        self.assertEqual(instructor_user.instructor.company, "company1")
        self.assertEqual(instructor_user.instructor.year, 0)


class GetUserPkTestCase(TestCase):
    client = Client()

    def setUp(self):
        part = User.objects.create_user(
            username="part",
            password="password",
            first_name="Kildong",
            last_name="Hong",
            email="part@mail.com",
        )
        self.part_token = 'Token ' + Token.objects.create(user=part).key
        self.part_id = part.id

        participant_profile = ParticipantProfile.objects.create(
            user=part,
            university="university1",
        )
        self.participant_profile_id = participant_profile.id

        inst = User.objects.create_user(
            username="inst",
            password="password",
            email="inst@mail.com",
        )
        self.inst_token = 'Token ' + Token.objects.create(user=inst).key
        self.inst_id = inst.id

        instructor_profile = InstructorProfile.objects.create(
            user=inst,
            company="company1",
        )
        self.instructor_profile_id = instructor_profile.id

        seminar = Seminar.objects.create(
            name="seminar1",
            capacity=10,
            count=5,
            time=datetime.time(hour=14, minute=30),
        )
        self.seminar_id = seminar.id

        UserSeminar.objects.create(
            user=part,
            seminar=seminar,
            role='participant',
            dropped_at=None,
        )

        UserSeminar.objects.create(
            user=inst,
            seminar=seminar,
            role='instructor',
            dropped_at=None,
        )

    def test_get_user_userid_unauthorized(self):
        response = self.client.get(         # Unauthorized
            '/api/v1/user/1/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_me_unauthorized(self):
        response = self.client.get(         # Unauthorized
            '/api/v1/user/me/',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_userid_wrong_pk(self):
        response = self.client.get(         # Wrong pk
            '/api/v1/user/3/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part_token
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_userid(self):
        response = self.client.get(         # Correct
            '/api/v1/user/{}/'.format(self.part_id),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.part_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.part_id)
        self.assertEqual(data["username"], "part")
        self.assertEqual(data["email"], "part@mail.com")
        self.assertEqual(data["first_name"], "Kildong")
        self.assertEqual(data["last_name"], "Hong")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertNotIn("token", data)

        participant = data["participant"]
        self.assertIsNotNone(participant)
        self.assertEqual(participant["id"], self.participant_profile_id)
        self.assertEqual(participant["university"], "university1")
        self.assertTrue(participant["accepted"])
        self.assertEqual(len(participant["seminars"]), 1)
        seminar = participant["seminars"][0]
        self.assertEqual(seminar["id"], self.seminar_id)
        self.assertEqual(seminar["name"], "seminar1")
        self.assertIn("joined_at", seminar)
        self.assertTrue(seminar["is_active"])
        self.assertIsNone(seminar["dropped_at"])

        self.assertIsNone(data["instructor"])

    def test_get_user_me(self):
        response = self.client.get(         # Correct
            '/api/v1/user/me/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.inst_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["id"], self.inst_id)
        self.assertEqual(data["username"], "inst")
        self.assertEqual(data["email"], "inst@mail.com")
        self.assertEqual(data["first_name"], "")
        self.assertEqual(data["last_name"], "")
        self.assertIn("last_login", data)
        self.assertIn("date_joined", data)
        self.assertNotIn("token", data)

        self.assertIsNone(data["participant"])

        instructor = data["instructor"]
        self.assertIsNotNone(instructor)
        self.assertEqual(instructor["id"], self.instructor_profile_id)
        self.assertEqual(instructor["company"], "company1")
        self.assertIsNone(instructor["year"])
        charge = instructor["charge"]
        self.assertIsNotNone(charge)
        self.assertEqual(charge["id"], self.seminar_id)
        self.assertEqual(charge["name"], "seminar1")
        self.assertIn("joined_at", charge)

