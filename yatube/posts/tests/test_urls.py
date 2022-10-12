from http import HTTPStatus

from django.urls import reverse

from .base_testcase import BaseTestCase


class PostURLsTests(BaseTestCase):
    def test_urls_exists_at_desired_location(self):
        for address, (_, user) in self.template_pages_name.items():
            with self.subTest(address=address):
                response = user.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, (template, user) in self.template_pages_name.items():
            with self.subTest(address=address):
                response = user.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_guest_client(self):
        """Редирект неавторизованного пользователя"""
        url1 = "/auth/login/?next=/create/"
        url2 = f"/auth/login/?next=/posts/{self.post.id}/edit/"

        pages = {
            reverse("posts:post_create"): url1,
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk}): url2,
        }

        for page, value in pages.items():
            response = self.client.get(page)
            self.assertRedirects(response, value)

    def test_urls_redirect_authorized_client(self):
        """Редирект авторизованного пользователя (не автора)
        при редактировании cтраницы"""
        response = self.auth_other_user.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.pk})
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post.pk}),
        )

    def test_unexisting_page_for_auth_users(self):
        """Не существующая страница отображает код HTTP 404."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_static_page_urls_at_desired_location(self):
        """Доступность статичных страниц"""
        static_page_urls = ["/about/author/", "/about/tech/"]

        for url in static_page_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
