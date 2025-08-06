import json
import os
import shutil
import tempfile
from xml.etree.ElementTree import indent

from django.test import TestCase

from DentsInspector.ai import GeminiAIEngine, ChatgptAIEngine
from DentsInspector.models import PLDS
import dotenv

dotenv.load_dotenv()

def _translate_plds(data_json):
    print(f"Translating {data_json}")
    translated = []
    for item in data_json:
        if not PLDS.objects.plds_exists(item["plds"]):
            continue
        trans_item = item.copy()
        trans_item["plds"] = PLDS.objects.json(trans_item["plds"])
        translated.append(trans_item)
    return translated


# class TestEventGemini(TestCase):
#
#     def setUp(self):
#         self.engine = GeminiAIEngine()
#
#     def _event_(self, event_number):
#         current_dir = os.path.dirname(__file__)
#         archive_path = os.path.join(current_dir, "data", f"event_{event_number}.zip")
#
#         response = self.engine.respond(archive_path)
#         translated = _translate_plds(response)
#         print(json.dumps({"event": event_number, "damages": translated}, indent=4))
#
#     def test_events(self):
#         event_numbers = [int(x) for x in os.environ.get('EVENTS').split(',')]
#         for event_number in event_numbers:
#             print(f"Testing event: {event_number}...\n")
#             self._event_(event_number)
#             print("Done\n")


class TestEventChatgpt(TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ChatgptAIEngine()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _event_(self, event_number):
        current_dir = os.path.dirname(__file__)
        archive_path = os.path.join(current_dir, "data", f"event_{event_number}.zip")

        response = self.engine.respond(archive_path)
        print(f"AI response: {response}")
        translated = _translate_plds(response)
        print(json.dumps({"event": event_number, "damages": translated}, indent=4))

    def test_events(self):
        event_numbers = [int(x) for x in os.environ.get('EVENTS').split(',')]
        for event_number in event_numbers:
            print(f"Testing event: {event_number}...\n")
            self._event_(event_number)
            print("Done\n")


