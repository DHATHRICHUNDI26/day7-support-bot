import logging

import app as bot


def test_chat_does_not_log_customer_details(caplog):
    with caplog.at_level(logging.INFO):
        response = bot.app.test_client().post(
            "/chat",
            json={
                "customer_email": "ravi.kumar@example.com",
                "message": "Where is my order 10231?",
            },
        )

    assert response.status_code == 200
    assert "Ravi Kumar" not in caplog.text
    assert "ravi.kumar@example.com" not in caplog.text
    assert "+91 98480 12345" not in caplog.text
    assert "Where is my order 10231?" not in caplog.text