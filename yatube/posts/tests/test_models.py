from django.conf import settings

from .base_testcase import BaseTestCase


class PostModelTest(BaseTestCase):
    def test_models_have_correct_object_names(self):
        """Метод __str__ в моделях Post, Group совпадает с ожидаемым."""
        post = PostModelTest.post
        group = PostModelTest.group

        expected_post_correct_name = post.text[: settings.CHAR_IN_WORD]
        expected_group_correct_name = group.title

        self.assertEqual(expected_post_correct_name, str(post))
        self.assertEqual(expected_group_correct_name, str(group))

    def test_post_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post

        field_verbose_text = {
            "text": "Текст поста",
            "pub_date": "Дата публикации",
            "author": "Автор",
            "group": "Группа",
        }

        for field, expected_value in field_verbose_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_post_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post

        expected_text_help_text = "Введите текст поста"
        expected_group_help_text = "Группа, к которой будет относиться пост"

        self.assertEqual(
            post._meta.get_field("text").help_text, expected_text_help_text
        )

        self.assertEqual(
            post._meta.get_field("group").help_text, expected_group_help_text
        )
