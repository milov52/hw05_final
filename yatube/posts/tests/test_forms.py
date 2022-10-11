import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from ..models import Comment, Post
from .base_testcase import BaseTestCase

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTest(BaseTestCase):
    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_post_create_form_auth_user(self):
        """Создание поста авторизованным пользователем."""
        post_count = Post.objects.count()

        uploaded = SimpleUploadedFile(
            name="small.gif", content=self.small_gif, content_type="image/gif"
        )

        form_data = {
            "author": self.user,
            "text": "Тестовый пост",
            "group": self.group.id,
            "image": uploaded,
        }

        redirect_url = reverse(
            "posts:profile", kwargs={"username": self.user.username}
        )

        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )

        post_obj = Post.objects.first()
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post_obj.text, form_data["text"])
        self.assertEqual(post_obj.group.id, form_data["group"])
        self.assertEqual(post_obj.author, self.user)
        self.assertEqual(post_obj.image, "posts/small.gif")

    def test_post_create_form_anonim_user(self):
        """
        У анонимного пользователя нет прав на создание записи
        Происходит редирект, новый пост не создается.
        """
        post_count = Post.objects.count()
        redirect_url = "/auth/login/?next=/create/"

        response = self.client.post(
            reverse("posts:post_create"), data=self.form_data, follow=True
        )

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertFalse(Post.objects.filter(text="Анонимный текст").exists())

    def test_post_edit_form_author(self):
        """Автор поста редактирует пост и отправляет правильную форму."""
        update_text = "Измененный текст"
        self.form_data["text"] = update_text

        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=self.form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, update_text)

    def test_post_edit_form_anonumis(self):
        """
        У анонимного пользователя нет прав на редактирование записи
        Происходит редирект, текст поста не меняется.
        """
        redirect_url = f"/auth/login/?next=/posts/{self.post.pk}/edit/"

        response = self.client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}),
            data=self.form_data,
            follow=True,
        )

        self.assertRedirects(response, redirect_url)
        self.assertFalse(Post.objects.filter(text="Анонимный текст").exists())

        @classmethod
        def tearDownClass(self):
            super().tearDownClass()
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class CommentFormTest(BaseTestCase):
    def test_comment_create_form_auth_user(self):
        """Добавление комментария авторизованным пользователем"""
        comment_count = Comment.objects.count()
        form_data = {
            "text": "Еще один тестовый комментарий",
            "author": self.user,
            "post": self.post,
        }
        redirect_url = reverse(
            "posts:post_detail", kwargs={"post_id": self.post.pk}
        )

        response = self.authorized_client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=form_data,
            follow=True,
        )

        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, redirect_url)

        comment = Comment.objects.get(text=form_data["text"])
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_comment_create_form_anonim_user(self):
        """
        У анонимного пользователя нет прав на создание комментария
        Происходит редирект, новый комментарий не добавляется.
        """
        comment_count = Comment.objects.count()
        redirect_url = f"/auth/login/?next=/posts/{self.post.pk}/comment/"

        response = self.client.post(
            reverse("posts:add_comment", kwargs={"post_id": self.post.pk}),
            data=self.form_data,
            follow=True,
        )

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertFalse(
            Comment.objects.filter(text="Анонимный текст").exists()
        )
