import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )

        cls.user = User.objects.create_user(username="test_user")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )

        cls.group2 = Group.objects.create(
            title="Группа",
            slug="test-slug2",
            description="Тестовое описание2",
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
            image=cls.uploaded,
        )

        cls.comment = Comment.objects.create(
            post=cls.post, author=cls.user, text="Тестовый комментарий"
        )

        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.other_user = User.objects.create_user(username="other_user")
        cls.auth_other_user = Client()
        cls.auth_other_user.force_login(cls.other_user)

        cls.form_data = {"text": "Анонимный текст"}

        cls.index_url = reverse("posts:index")
        cls.group_url = reverse(
            "posts:group_list", kwargs={"slug": cls.group.slug}
        )
        cls.profile_url = reverse(
            "posts:profile", kwargs={"username": cls.user}
        )
        cls.post_detail_url = reverse(
            "posts:post_detail", kwargs={"post_id": cls.post.pk}
        )
        cls.post_create_url = reverse("posts:post_create")
        cls.post_edit_url = reverse(
            "posts:post_edit", kwargs={"post_id": cls.post.pk}
        )
        cls.follow_index_url = reverse("posts:follow_index")
        cls.profile_follow_url = reverse(
            "posts:profile_follow", kwargs={"username": cls.user}
        )
        cls.profile_unfollow_url = reverse(
            "posts:profile_unfollow", kwargs={"username": cls.user}
        )

        cls.template_pages_name = {
            cls.index_url: (
                "posts/index.html",
                cls.authorized_client,
            ),
            cls.group_url: (
                "posts/group_list.html",
                cls.authorized_client,
            ),
            cls.profile_url: (
                "posts/profile.html",
                cls.authorized_client,
            ),
            cls.post_detail_url: (
                "posts/post_detail.html",
                cls.authorized_client,
            ),
            cls.post_edit_url: (
                "posts/create_post.html",
                cls.authorized_client,
            ),
            cls.post_create_url: (
                "posts/create_post.html",
                cls.auth_other_user,
            ),
        }

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
