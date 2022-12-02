from django import forms
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from ..apps import PostsConfig

from ..models import Follow, Group, Post, User
from .base_testcase import BaseTestCase


class PostViewsTest(BaseTestCase):
    def assert_page_obj(self, response):
        first_page = response.context.get("page_obj")[0]
        self.assertEqual(first_page.text, self.post.text)
        self.assertEqual(first_page.author, self.user)
        self.assertEqual(first_page.group.slug, self.group.slug)
        self.assertEqual(
            first_page.image, f"{PostsConfig.name}/{self.uploaded.name}"
        )

    def test_pages_used_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, (
            template,
            client,
        ) in self.template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index_url)
        self.assert_page_obj(response=response)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.group_url)

        self.assertEqual(
            response.context.get("group").title, "Тестовая группа"
        )
        self.assert_page_obj(response=response)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.profile_url)
        self.assert_page_obj(response=response)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_detail_url)
        self.assertEqual(response.context.get("post").text, "Тестовый пост")
        self.assertEqual(response.context.get("post").author, self.user)
        self.assertEqual(response.context.get("post").image, "posts/small.gif")
        self.assertEqual(
            response.context.get("comments")[0].text, self.comment.text
        )

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильной формой"""
        response = self.authorized_client.get(self.post_create_url)

        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post edit сформирован с правильной формой"""
        response = self.authorized_client.get(self.post_edit_url)

        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cache(self):
        """Шаблон index работает с кеш."""
        get_content = self.authorized_client.get(self.index_url).content
        response = get_content
        self.post.delete()
        response_cache = get_content
        self.assertEqual(response, response_cache)
        cache.clear()
        response_clear = self.authorized_client.get(get_content)
        self.assertNotEqual(response, response_clear)


class PaginatorViewsTest(BaseTestCase):
    def test_paginator_views(self):
        Post.objects.bulk_create(
            [
                Post(
                    author=self.user,
                    text=f"Тестовый пост {i}",
                    group=self.group,
                )
                for i in range(settings.POST_ON_PAGE + 3)
            ]
        )

        second_page = "?page=2"
        records_on_first_page = settings.POST_ON_PAGE
        records_on_second_page = Post.objects.count() - records_on_first_page

        template_paginator = [
            (self.index_url, records_on_first_page),
            (self.index_url + second_page, records_on_second_page),
            (self.group_url, settings.POST_ON_PAGE),
            (self.group_url + second_page, records_on_second_page),
        ]

        for (page, count_pages) in template_paginator:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(
                    len(response.context["page_obj"]), count_pages
                )


class FollowViewsTest(BaseTestCase):
    def test_auth_user_can_follow_authors(self):
        """Тестирование подписки и отписки авторизованного пользователя"""

        follow_count = Follow.objects.count()
        redirect_url = self.profile_url

        response = self.auth_other_user.get(self.profile_follow_url)

        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count + 1)

        response = self.auth_other_user.get(self.profile_unfollow_url)
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Follow.objects.count(), follow_count)

    def assertFollow(self):
        response = self.authorized_client.get(self.follow_index_url)
        content_count = len(response.context["page_obj"])
        self.assertEqual(content_count, Follow.objects.count())

    def test_show_posts_to_followers(self):
        self.authorized_client.get(self.profile_follow_url)
        self.assertFollow()

    def test_show_posts_to_not_followers(self):
        self.assertFollow()
