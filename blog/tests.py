from pathlib import Path
from django.test import SimpleTestCase, RequestFactory
from django.template.loader import render_to_string


class FooterSpacingTests(SimpleTestCase):
    def test_base_does_not_push_footer_to_viewport_bottom(self):
        source = (Path(__file__).resolve().parents[1] / 'templates' / 'base.html').read_text()
        self.assertNotIn('h-100', source)
        self.assertNotIn('footer mt-auto', source)
        self.assertIn('footer mt-4 py-3 dark-bg', source)

    def test_short_content_uses_same_content_following_footer(self):
        html = render_to_string('base.html', {'messages': []})
        self.assertIn('<footer class="footer mt-4 py-3 dark-bg">', html)
        self.assertLess(html.index('</main>'), html.index('<footer'))
        self.assertNotIn('h-100', html)

    def test_all_content_templates_inherit_content_following_shell(self):
        root = Path(__file__).resolve().parents[1] / 'templates'
        for name in ['index.html', 'post_detail.html', 'post_create.html', 'post_edit.html', 'post_delete.html', 'post_contact.html', 'account/login.html', 'account/signup.html']:
            with self.subTest(template=name):
                source = (root / name).read_text()
                self.assertIn('extends', source)
                self.assertIn('base.html', source)
                self.assertNotIn('mt-auto', source)

    def test_comment_column_is_only_rendered_when_it_has_content(self):
        from types import SimpleNamespace
        from django.contrib.auth.models import AnonymousUser
        source = (Path(__file__).resolve().parents[1] / 'templates' / 'post_detail.html').read_text()
        self.assertIn('{% if commented or user.is_authenticated %}', source)
        from blog.forms import CommentForm
        request = RequestFactory().get('/synthetic-audit/')
        post = SimpleNamespace(slug='synthetic-audit', title='Synthetic post', author='Synthetic author', content='Synthetic content', featured_image=SimpleNamespace(url='placeholder'), number_of_likes=0)
        for authenticated, commented in [(False, False), (True, False), (False, True)]:
            with self.subTest(authenticated=authenticated, commented=commented):
                user = SimpleNamespace(is_authenticated=True, username='synthetic') if authenticated else AnonymousUser()
                html = render_to_string('post_detail.html', {'post': post, 'user': user, 'commented': commented, 'comments': [], 'comment_form': CommentForm()}, request=request)
                self.assertEqual('col-md-4 card mb-4 mt-3' in html, authenticated or commented)
                if authenticated and not commented:
                    self.assertIn('Leave a comment:', html)
                if commented:
                    self.assertIn('Your comment is awaiting approval', html)
