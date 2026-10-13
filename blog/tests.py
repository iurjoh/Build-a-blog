from pathlib import Path
from django.test import SimpleTestCase
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
