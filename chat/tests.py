from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import UserProfile

from .models import ChatMessage, ChatRoom, KnowledgeDocument


@override_settings(OPENAI_API_KEY="")
class ChatFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="strong-test-pass-123",
        )
        UserProfile.objects.create(user=self.user, email=self.user.email)
        KnowledgeDocument.objects.create(
            title="測試規範",
            doc_type="policy",
            tags="安全",
            content="先同理，再給小步驟。",
        )

    def test_register_creates_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "new_user",
                "email": "new@example.com",
                "phone_number": "0912345678",
                "password1": "complex-test-pass-123",
                "password2": "complex-test-pass-123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProfile.objects.filter(user__username="new_user").exists())

    def test_chat_post_saves_messages_and_markdown(self):
        self.client.login(username="student", password="strong-test-pass-123")
        response = self.client.post(reverse("chat_home"), {"message": "我最近壓力很大"})

        self.assertEqual(response.status_code, 302)
        room = ChatRoom.objects.get(user=self.user)
        self.assertEqual(ChatMessage.objects.filter(room=room).count(), 2)
        first_message = ChatMessage.objects.filter(room=room).first()
        self.assertTrue(first_message.markdown_backup_path.endswith(f"{room.id}.md"))

    def test_chat_post_accepts_supported_photo_upload(self):
        self.client.login(username="student", password="strong-test-pass-123")
        image = SimpleUploadedFile(
            "photo.png",
            (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
                b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05"
                b"\xfe\x02\xfeA\xe2!\xbc\x00\x00\x00\x00IEND\xaeB`\x82"
            ),
            content_type="image/png",
        )

        response = self.client.post(reverse("chat_home"), {"message": "看看這張照片", "attachment": image})

        self.assertEqual(response.status_code, 302)
        user_message = ChatMessage.objects.filter(role="user").first()
        self.assertTrue(user_message.uploaded_file.name)

    def test_chat_post_rejects_unsupported_photo_format(self):
        self.client.login(username="student", password="strong-test-pass-123")
        image = SimpleUploadedFile("photo.heic", b"not-real-heic", content_type="image/heic")

        response = self.client.post(reverse("chat_home"), {"message": "看看這張照片", "attachment": image})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ChatMessage.objects.count(), 0)

    def test_chat_api_requires_login(self):
        response = Client().post(
            reverse("chat_api"),
            data={"message": "hello"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)

    def test_chat_api_saves_reply(self):
        self.client.login(username="student", password="strong-test-pass-123")
        response = self.client.post(
            reverse("chat_api"),
            data={"message": "我和伴侶吵架了"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ChatMessage.objects.count(), 2)
        self.assertIn("answer", response.json())

    def test_settings_update_profile_and_visual_preferences(self):
        self.client.login(username="student", password="strong-test-pass-123")
        response = self.client.post(
            reverse("update_profile"),
            {
                "email": "student2@example.com",
                "phone_number": "0987654321",
            },
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse("update_visual_preferences"),
            {
                "preferred_theme_color": "rose",
                "custom_accent_color": "#b64b68",
                "font_scale": "large",
                "chat_density": "spacious",
                "visual_effect": "snow",
                "bubble_style": "soft",
            },
        )

        self.assertEqual(response.status_code, 302)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.email, "student2@example.com")
        self.assertEqual(profile.preferred_theme_color, "rose")
        self.assertEqual(profile.custom_accent_color, "#b64b68")
        self.assertEqual(profile.visual_effect, "snow")

    def test_delete_room_only_removes_owned_room(self):
        self.client.login(username="student", password="strong-test-pass-123")
        room = ChatRoom.objects.create(user=self.user, title="要刪掉")
        ChatMessage.objects.create(room=room, user=self.user, role="user", content="測試")

        response = self.client.post(reverse("delete_room", args=[room.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ChatRoom.objects.filter(id=room.id).exists())
