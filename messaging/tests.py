import json
from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from messaging.models import MessageLog


@override_settings(META_APP_SECRET="")  # signature validation disabled in this test
class WebhookTests(TestCase):
    def test_webhook_creates_message_log(self):
        user = User.objects.create_user(email="biz@example.com", password="pass12345", whatsapp_phone_number_id="123")

        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "WABA_ID",
                    "changes": [
                        {
                            "value": {
                                "metadata": {"display_phone_number": "15551234567", "phone_number_id": "123"},
                                "messages": [
                                    {
                                        "from": "15550001111",
                                        "id": "wamid.ID",
                                        "timestamp": str(int(timezone.now().timestamp())),
                                        "text": {"body": "Hi, what are your hours?"},
                                        "type": "text",
                                    }
                                ],
                            },
                            "field": "messages",
                        }
                    ],
                }
            ],
        }

        res = self.client.post("/webhook/", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(MessageLog.objects.filter(business=user).count(), 1)

