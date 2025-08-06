import json
import os
import re
import shutil
import tarfile
import tempfile
import zipfile
from typing import Dict

from dotenv import load_dotenv
import base64
import logging
import openai
from openai import OpenAI
from google.api_core import exceptions

from DentsInspector.ai.instructions import get_system_instructions as SYSTEM_INSTRUCTIONS_BUILDER
from .roles import *

load_dotenv()
logger = logging.getLogger("open_vally")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _encode_image_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class AIEngine:
    """
    A class to manage interactions with OpenAI's VLM models (e.g., GPT-4o),
    with archive handling integrated into the image processing method.
    """

    def __init__(self, initial_instructions: str = None, temp_dir: str = None):
        self._instructions = initial_instructions or SYSTEM_INSTRUCTIONS_BUILDER()
        self.temp_dir = temp_dir  # Provided by test or app. If None, one will be created.

    def _generate_image_parts(self, archive_path: str) -> Dict[str, str]:
        """
        Extract image files from archive and return dict: {filename: image_file_path}
        """
        temp_dir = self.temp_dir or tempfile.mkdtemp()
        image_parts_dict = {}

        try:
            if archive_path.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            elif archive_path.endswith((".tar", ".tar.gz", ".tgz")):
                with tarfile.open(archive_path, "r") as tar_ref:
                    tar_ref.extractall(temp_dir)
            else:
                raise ValueError("Unsupported archive format. Use .zip or .tar")

            for dirpath, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    image_parts_dict[filename] = file_path

            return image_parts_dict

        except FileNotFoundError:
            raise FileNotFoundError(f"Archive file not found: {archive_path}")
        except (tarfile.TarError, zipfile.BadZipFile) as e:
            raise ValueError(f"Corrupt archive: {e}")
        except exceptions.GoogleAPIError as e:
            logger.error(f"Unexpected error: {e}")
            raise e

    def respond(self, archive_path: str) -> str:
        try:
            image_parts = self._generate_image_parts(archive_path)

            messages = [{"role": "system", "content": self._instructions}]

            for filename, file_path in image_parts.items():
                image_base64 = _encode_image_to_base64(file_path)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Inspect this image: {filename}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                })

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.2,
            )

            ai_response_text = response.choices[0].message.content
            ai_response_text = re.sub(r'```json\n(.*?)```', r'\1', ai_response_text, flags=re.DOTALL).strip()
            return json.loads(ai_response_text)

        except Exception as e:
            logger.error(f"Error using OpenAI API: {e}")
            return f"Error: {e}"
