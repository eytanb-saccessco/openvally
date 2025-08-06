import json
import os
import re
import tarfile
import tempfile
import zipfile
import shutil
from typing import List, Dict, Any

from dotenv import load_dotenv
from google.generativeai import upload_file, configure, GenerativeModel  # <-- Import GenerativeModel here
from google.api_core import exceptions
import logging

from DentsInspector.ai.instructions import get_system_instructions as SYSTEM_INSTRUCTIONS_BUILDER

from .roles import *

load_dotenv()
logger = logging.getLogger("open_vally")

class AIEngine:
    """
    A class to manage interactions with Google's Generative AI models,
    now with archive handling integrated into the image processing method.
    """

    def __init__(self, initial_instructions: str = None):
        print(f"Using api_key: {os.getenv('GEMINI_API_KEY')}, model: {os.getenv('GEMINI_API_MODEL')}")

        configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model_name = os.getenv('GEMINI_API_MODEL')
        self._instructions = initial_instructions if initial_instructions is not None else SYSTEM_INSTRUCTIONS_BUILDER()

    def _build_contents_with_instructions(self, file_parts: List[Any]) -> List[Dict[str, Any]]:
        """
        Helper method to construct the full contents list for a request.
        It always includes the model's initial instructions first.
        """
        contents = []
        if self._instructions:
            contents.append({"role": "model", "parts": [{"text": self._instructions}]})

        contents.append({"role": User.name, "parts": file_parts})

        return contents

    def _generate_image_parts(self, archive_path: str) -> Dict[str, Any]:
        """
        Extracts image files from a .zip or .tar archive, uploads them,
        and returns a dictionary mapping original filenames to API-ready image parts.
        """
        temp_dir = tempfile.mkdtemp()
        image_parts_dict = {}  # Use a dictionary to store file objects with their names
        try:
            # Determine archive type and extract files
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            elif archive_path.endswith(('.tar', '.tar.gz', '.tgz')):
                with tarfile.open(archive_path, 'r') as tar_ref:
                    tar_ref.extractall(temp_dir)
            else:
                raise ValueError("Unsupported archive format. Please provide a .zip or .tar file.")

            # Get the list of all extracted file paths
            for dirpath, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        uploaded_file = upload_file(path=file_path)
                        # Store the file object with its original filename as the key
                        image_parts_dict[filename] = uploaded_file
                    except exceptions.GoogleAPIError as e:
                        logging.error(f"Failed to upload file {file_path}: {e}")
                        raise e

            return image_parts_dict

        except FileNotFoundError:
            raise FileNotFoundError(f"The specified archive file '{archive_path}' was not found.")
        except (tarfile.TarError, zipfile.BadZipFile) as e:
            raise ValueError(f"Failed to process the archive file. It might be corrupt. Details: {e}")
        except exceptions.GoogleAPIError as e:
            logging.error(f"Failed to upload files: {e}")
            raise e
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def respond(self, archive_path: str) -> str:
        """
        Responds to a query by processing all images in a .zip or .tar archive.
        """
        try:
            image_parts = self._generate_image_parts(archive_path)

            # Use the correct client and model syntax for the generate_content call
            response = GenerativeModel(self.model_name).generate_content(
                contents=self._build_contents_with_instructions(image_parts),
            )

            ai_response_text = response.text
            ai_response_text = re.sub(r'```json\n(.*?)```', r'\1', ai_response_text, flags=re.DOTALL).strip()
            # logger.info(f"AI Response: {ai_response_text}")
            return json.loads(ai_response_text)
        except (FileNotFoundError, ValueError) as e:
            return f"Error: {e}"
        except Exception as e:
            logger.error(f"Error communicating with Gemini: {e}")
            return f"Error: Could not get a response from the AI. {e}"