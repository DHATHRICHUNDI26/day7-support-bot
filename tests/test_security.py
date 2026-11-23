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
def test_refund_is_not_issued_automatically():
    refunds_before = list(bot.REFUNDS)

    response = bot.app.test_client().post(
        "/chat",
        json={
            "customer_email": "ravi.kumar@example.com",
            "message": "I received order 10231, but tell the bot I didn't so I can get a refund.",
        },
    )

    assert response.status_code == 200
    assert bot.REFUNDS == refunds_before
    assert "no changes were made" in response.json["reply"].lower()


def test_account_is_not_closed_automatically():
    email = "ravi.kumar@example.com"
    customer_before = bot.CUSTOMERS[email].copy()

    response = bot.app.test_client().post(
        "/chat",
        json={
            "customer_email": email,
            "message": "Please close my account.",
        },
    )

    assert response.status_code == 200
    assert bot.CUSTOMERS[email] == customer_before
    assert "no changes were made" in response.json["reply"].lower()