from unittest.mock import Mock, patch

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.test import SimpleTestCase, override_settings

from apps.common.services.emails_sending import EmailService


class SendEmailTestCase(SimpleTestCase):
    """Tests for ``EmailService.send``."""

    def setUp(self):
        self.template_name = "welcome"
        self.recipients = ["test@example.com"]
        self.context = {"user_name": "John Doe"}
        self.from_email = "sender@example.com"

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_success(self, mock_email_class, mock_render):
        mock_render.side_effect = [
            "Welcome to our platform",
            "Welcome John Doe!",
            "<h1>Welcome John Doe!</h1>",
        ]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=self.recipients,
            context=self.context,
            from_email=self.from_email,
        )

        expected_context = {
            **self.context,
            "site_url": settings.SITE_URL,
            "project_name": settings.PROJECT_NAME,
        }
        mock_render.assert_any_call(
            "emails/welcome/subject.txt", context=expected_context
        )
        mock_render.assert_any_call(
            "emails/welcome/body.txt", context=expected_context
        )
        mock_render.assert_any_call(
            "emails/welcome/body.html", context=expected_context
        )
        mock_email_class.assert_called_once_with(
            subject="Welcome to our platform",
            body="Welcome John Doe!",
            from_email=self.from_email,
            to=self.recipients,
        )
        mock_email_instance.attach_alternative.assert_called_once_with(
            "<h1>Welcome John Doe!</h1>", "text/html"
        )
        mock_email_instance.send.assert_called_once()

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_with_string_recipient(
        self, mock_email_class, mock_render
    ):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients="single@example.com",
            context=self.context,
        )

        call_args = mock_email_class.call_args
        self.assertEqual(call_args[1]["to"], ["single@example.com"])

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_with_none_context(self, mock_email_class, mock_render):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=self.recipients,
            context=None,
        )

        expected_context = {
            "site_url": settings.SITE_URL,
            "project_name": settings.PROJECT_NAME,
        }
        mock_render.assert_any_call(
            "emails/welcome/subject.txt", context=expected_context
        )

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    @override_settings(DEFAULT_FROM_EMAIL="default@example.com")
    def test_send_email_with_default_from_email(
        self, mock_email_class, mock_render
    ):
        """Falls back to DEFAULT_FROM_EMAIL when from_email is None."""
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=self.recipients,
            context=self.context,
            from_email=None,
        )

        call_args = mock_email_class.call_args
        self.assertEqual(call_args[1]["from_email"], "default@example.com")

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_context_extension(self, mock_email_class, mock_render):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=self.recipients,
            context={"custom_var": "custom_value"},
        )

        expected_context = {
            "custom_var": "custom_value",
            "site_url": settings.SITE_URL,
            "project_name": settings.PROJECT_NAME,
        }
        for call in mock_render.call_args_list:
            self.assertEqual(call[1]["context"], expected_context)

    @patch("apps.common.services.emails_sending.render_to_string")
    def test_send_email_template_not_found(self, mock_render):
        mock_render.side_effect = TemplateDoesNotExist("Template not found")

        with self.assertRaises(TemplateDoesNotExist):
            EmailService.send(
                template_name="nonexistent",
                recipients=self.recipients,
                context=self.context,
            )

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_multiple_recipients(
        self, mock_email_class, mock_render
    ):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        multiple_recipients = [
            "user1@example.com",
            "user2@example.com",
            "user3@example.com",
        ]
        EmailService.send(
            template_name=self.template_name,
            recipients=multiple_recipients,
            context=self.context,
        )

        call_args = mock_email_class.call_args
        self.assertEqual(call_args[1]["to"], multiple_recipients)

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_subject_stripped(self, mock_email_class, mock_render):
        mock_render.side_effect = [
            "  Subject with whitespace  \n",
            "Text content",
            "HTML content",
        ]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=self.recipients,
            context=self.context,
        )

        call_args = mock_email_class.call_args
        self.assertEqual(call_args[1]["subject"], "Subject with whitespace")

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_template_paths(self, mock_email_class, mock_render):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name="password_reset",
            recipients=self.recipients,
            context=self.context,
        )

        rendered_paths = [call[0][0] for call in mock_render.call_args_list]
        self.assertEqual(
            rendered_paths,
            [
                "emails/password_reset/subject.txt",
                "emails/password_reset/body.txt",
                "emails/password_reset/body.html",
            ],
        )

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_propagates_send_errors(
        self, mock_email_class, mock_render
    ):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_instance.send.side_effect = Exception("SMTP Error")
        mock_email_class.return_value = mock_email_instance

        with self.assertRaisesRegex(Exception, "SMTP Error"):
            EmailService.send(
                template_name=self.template_name,
                recipients=self.recipients,
                context=self.context,
            )

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    @override_settings(
        SITE_URL="https://testdomain.com", PROJECT_NAME="Test Project"
    )
    def test_send_email_settings_injection(
        self, mock_email_class, mock_render
    ):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=self.recipients,
            context={"custom": "value"},
        )

        expected_context = {
            "custom": "value",
            "site_url": "https://testdomain.com",
            "project_name": "Test Project",
        }
        for call in mock_render.call_args_list:
            self.assertEqual(call[1]["context"], expected_context)

    @patch("apps.common.services.emails_sending.render_to_string")
    @patch("apps.common.services.emails_sending.EmailMultiAlternatives")
    def test_send_email_empty_recipients_list(
        self, mock_email_class, mock_render
    ):
        mock_render.side_effect = ["Subject", "Text content", "HTML content"]
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance

        EmailService.send(
            template_name=self.template_name,
            recipients=[],
            context=self.context,
        )

        call_args = mock_email_class.call_args
        self.assertEqual(call_args[1]["to"], [])
        mock_email_instance.send.assert_called_once()
