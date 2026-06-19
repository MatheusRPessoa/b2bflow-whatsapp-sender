from unittest.mock import patch, Mock

import pytest
import requests

from main import is_valid_phone, send_whatsapp_message


class TestIsValidPhone:
    def test_accepts_valid_digits_only_phone(self):
        assert is_valid_phone("5511999990001") is True

    def test_rejects_phone_with_plus_sign(self):
        assert is_valid_phone("+5511999990001") is False

    def test_rejects_phone_too_short(self):
        assert is_valid_phone("123") is False

    def test_rejects_phone_with_letters(self):
        assert is_valid_phone("55119999900a1") is False

    def test_rejects_empty_phone(self):
        assert is_valid_phone("") is False


class TestSendWhatsappMessage:
    @patch.dict("os.environ", {"ZAPI_INSTANCE_ID": "inst123", "ZAPI_TOKEN": "tok123"})
    @patch("main.requests.post")
    def test_returns_true_on_success(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"messageId": "abc123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = send_whatsapp_message("5511999990001", "Olá")

        assert result is True
        mock_post.assert_called_once()

    @patch.dict("os.environ", {"ZAPI_INSTANCE_ID": "inst123", "ZAPI_TOKEN": "tok123"})
    @patch("main.requests.post")
    def test_returns_false_on_http_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        result = send_whatsapp_message("5511999990001", "Olá")

        assert result is False

    @patch.dict("os.environ", {"ZAPI_INSTANCE_ID": "inst123", "ZAPI_TOKEN": "tok123"})
    @patch("main.requests.post")
    def test_returns_false_on_connection_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("network down")

        result = send_whatsapp_message("5511999990001", "Olá")

        assert result is False

    @patch.dict("os.environ", {}, clear=True)
    def test_raises_when_env_vars_missing(self):
        with pytest.raises(EnvironmentError):
            send_whatsapp_message("5511999990001", "Olá")
