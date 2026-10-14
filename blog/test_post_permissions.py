"""Authorization regression tests using invented accounts and posts only."""
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from .models import Post


class PostPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('synthetic-owner')
        cls.other = User.objects.create_user('synthetic-other')
        cls.post = Post.objects.create(
            title='Synthetic original', slug='synthetic-original',
            author=cls.owner, content='Synthetic content', status=1,
            featured_image='placeholder')

    def setUp(self):
        # Rendering the upload widget must not need cloud credentials or networking.
        image_url = patch('cloudinary.CloudinaryResource.build_url', return_value='https://example.invalid/synthetic-image.jpg')
        image_url.start()
        self.addCleanup(image_url.stop)

    def payload(self):
        return {'title': 'Synthetic changed', 'content': 'Updated synthetic content',
                'excerpt': 'Synthetic excerpt', 'featured_image': '',
                'author': self.other.pk, 'status': 0}

    def assert_original(self):
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.title, 'Synthetic original')
        self.assertEqual(post.content, 'Synthetic content')
        self.assertEqual(post.author_id, self.owner.pk)
        self.assertEqual(post.status, 1)
        self.assertEqual(Post.objects.count(), 1)

    def test_anonymous_create_get_and_post_require_login(self):
        url = reverse('post_create')
        for method in ['get', 'post']:
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, self.payload() if method == 'post' else {})
                self.assertEqual(response.status_code, 302)
                self.assertIn('/accounts/login/', response.url)
                self.assertIn('next=', response.url)
                self.assert_original()

    def test_anonymous_edit_and_delete_require_login(self):
        for route in ['post_edit', 'post_delete']:
            for method in ['get', 'post']:
                with self.subTest(route=route, method=method):
                    url = reverse(route, args=[self.post.slug])
                    response = getattr(self.client, method)(url, self.payload() if method == 'post' else {})
                    self.assertEqual(response.status_code, 302)
                    self.assertIn('/accounts/login/', response.url)
                    self.assert_original()

    def test_other_user_cannot_read_or_mutate_owner_post(self):
        self.client.force_login(self.other)
        for route in ['post_edit', 'post_delete']:
            for method in ['get', 'post']:
                with self.subTest(route=route, method=method):
                    response = getattr(self.client, method)(
                        reverse(route, args=[self.post.slug]),
                        self.payload() if method == 'post' else {})
                    self.assertEqual(response.status_code, 403)
                    self.assert_original()

    def test_owner_can_open_create_and_edit_forms(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('post_create')).status_code, 200)
        self.assertEqual(self.client.get(reverse('post_edit', args=[self.post.slug])).status_code, 200)

    def test_create_assigns_authenticated_user_not_forged_author(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('post_create'), self.payload())
        self.assertEqual(response.status_code, 302)
        created = Post.objects.get(slug='synthetic-changed')
        self.assertEqual(created.author_id, self.owner.pk)
        self.assertEqual(created.status, 1)

    def test_owner_can_edit_without_changing_author(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('post_edit', args=[self.post.slug]), self.payload())
        self.assertEqual(response.status_code, 302)
        changed = Post.objects.get(pk=self.post.pk)
        self.assertEqual(changed.title, 'Synthetic changed')
        self.assertEqual(changed.author_id, self.owner.pk)
        self.assertEqual(changed.status, 1)

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('post_delete', args=[self.post.slug]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_get_delete_never_deletes(self):
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(reverse('post_delete', args=[self.post.slug])).status_code, 405)
        self.assert_original()

    def test_missing_posts_return_404_for_signed_in_user(self):
        self.client.force_login(self.owner)
        for route in ['post_edit', 'post_delete']:
            for method in ['get', 'post']:
                with self.subTest(route=route, method=method):
                    response = getattr(self.client, method)(reverse(route, args=['missing-synthetic']))
                    self.assertEqual(response.status_code, 404)
        self.assert_original()

    def test_owner_writes_still_require_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        for route, args in [('post_create', []), ('post_edit', [self.post.slug]), ('post_delete', [self.post.slug])]:
            with self.subTest(route=route):
                self.assertEqual(client.post(reverse(route, args=args), self.payload()).status_code, 403)
                self.assert_original()
