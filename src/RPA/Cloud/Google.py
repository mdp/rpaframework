from functools import wraps
import logging
from typing import Any

try:
    from google.cloud import vision
    from google.cloud import language_v1
    from google.cloud.language_v1 import enums
    from google.protobuf.json_format import MessageToJson
    from google.cloud import storage
    from google.cloud import videointelligence
    from google.cloud import translate_v3
    from google.cloud import texttospeech_v1
    from google.cloud.texttospeech_v1.types import (
        AudioConfig,
        VoiceSelectionParams,
        SynthesisInput,
    )
    from google.cloud import speech

    HAS_GOOGLECLOUD = True
except ImportError:
    HAS_GOOGLECLOUD = False


def google_dependency_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not HAS_GOOGLECLOUD:
            raise ValueError(
                "Please install optional `google` package, "
                "`pip install rpaframework[google]` to use RPA.Cloud.Google library"
            )
        return f(*args, **kwargs)

    return wrapper


class GoogleBase:
    """Google base class for generic methods"""

    logger = None
    services: list = []
    clients: dict = {}
    region: str = None

    def _get_client_for_service(self, service_name: str = None):
        """Return client instance for servive if it has been initialized.

        :param service_name: name of the AWS service
        :return: client instance
        """
        if service_name not in self.clients.keys():
            raise KeyError(
                "Google service %s has not been initialized" % service_name.upper()
            )
        return self.clients[service_name]

    def _set_service(self, service_name: str = None, client: Any = None):
        self.clients[service_name] = client

    @google_dependency_required
    def _write_json(self, json_file, response):
        if json_file and response:
            with open(json_file, "w") as f:
                f.write(MessageToJson(response))


class ServiceVision(GoogleBase):
    """Class for Google Cloud Vision API

    Link to `Vision PyPI`_ page.

    .. _Vision PyPI: https://pypi.org/project/google-cloud-vision/
    """

    __service_name = "vision"

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceVision init")

    @google_dependency_required
    def init_vision_client(self, service_credentials_file: str = None) -> None:
        """Initialize Google Vision client
        """
        client = vision.ImageAnnotatorClient.from_service_account_json(
            service_credentials_file
        )
        self._set_service(self.__service_name, client)

    @google_dependency_required
    def _get_google_image(self, image_file):
        if not image_file:
            raise KeyError("image_file is required for parameter")
        with open(image_file, "rb") as f:
            content = f.read()
        return vision.types.Image(content=content)  # pylint: disable=E1101

    @google_dependency_required
    def detect_labels(self, image_file: str, json_file: str = None) -> dict:
        """Detect labels in the image

        :param image_file: source image file
        :param json_file: json target to save result, defaults to None
        :return: detection response
        """
        client = self._get_client_for_service(self.__service_name)
        image = self._get_google_image(image_file)
        response = client.label_detection(image=image)
        self._write_json(json_file, response)
        return response

    @google_dependency_required
    def detect_text(self, image_file: str, json_file: str = None) -> dict:
        """Detect text in the image

        :param image_file: source image file
        :param json_file: json target to save result, defaults to None
        :return: detection response
        """
        client = self._get_client_for_service(self.__service_name)
        image = self._get_google_image(image_file)
        response = client.text_detection(image=image)
        self._write_json(json_file, response)
        return response

    @google_dependency_required
    def detect_document(self, image_file: str, json_file: str = None) -> dict:
        """Detect document

        :param image_file: source image file
        :param json_file: json target to save result, defaults to None
        :return: detection response
        """
        client = self._get_client_for_service(self.__service_name)
        image = self._get_google_image(image_file)
        response = client.document_text_detection(image=image)
        self._write_json(json_file, response)
        return response

    @google_dependency_required
    def annotate_image(self, image_uri: str, json_file: str = None) -> dict:
        """Annotate image

        :param image_file: source image file
        :param json_file: json target to save result, defaults to None
        :return: detection response
        """
        client = self._get_client_for_service(self.__service_name)
        response = client.annotate_image(
            {"image": {"source": {"image_uri": image_uri}}}
        )
        self._write_json(json_file, response)
        return response

    @google_dependency_required
    def face_detection(self, image_uri: str, json_file: str = None) -> dict:
        """Detect faces

        :param image_uri: Google Cloud Storage URI
        :param json_file: json target to save result, defaults to None
        :return: detection response
        """
        client = self._get_client_for_service(self.__service_name)
        response = client.face_detection({"source": {"image_uri": image_uri}})
        self._write_json(json_file, response)
        return response


class ServiceNaturalLanguage(GoogleBase):
    """Class for Google Cloud Natural Language API

    Link to `Natural Language PyPI`_ page.

    .. _Natural Language PyPI: https://pypi.org/project/google-cloud-language/
    """

    __service_name = "natural-language"

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceNaturalLanguage init")

    @google_dependency_required
    def init_natural_language_client(
        self, service_credentials_file: str = None
    ) -> None:
        """Initialize Google Natural Language client
        """
        client = language_v1.LanguageServiceClient.from_service_account_json(
            service_credentials_file
        )
        self._set_service(self.__service_name, client)

    @google_dependency_required
    def analyze_sentiment(
        self, text_file: str, file_type: str = "text", json_file: str = None, lang=None
    ) -> dict:
        """Analyze sentiment in a text file

        :param text_file: source text file
        :param json_file: json target to save result, defaults to None
        :param lang: language code of the source, defaults to None
        :return: analysis response
        """
        client = self._get_client_for_service(self.__service_name)
        with open(text_file, "r") as f:
            text_content = f.read()
        # Available types: PLAIN_TEXT, HTML
        if file_type == "text":
            type_ = enums.Document.Type.PLAIN_TEXT
        else:
            type_ = enums.Document.Type.HTML
        document = {"content": text_content, "type": type_}
        # Optional. If not specified, the language is automatically detected.
        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        if lang is not None:
            document["language"] = lang
        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = enums.EncodingType.UTF8
        response = client.analyze_sentiment(document, encoding_type=encoding_type)
        self._write_json(json_file, response)
        return response

    @google_dependency_required
    def classify_text(self, text_file, json_file, lang=None):
        """Classify text

        :param text_file: source text file
        :param json_file: json target to save result, defaults to None
        :param lang: language code of the source, defaults to None
        :return: classify response
        """
        client = self._get_client_for_service(self.__service_name)
        with open(text_file, "r") as f:
            text_content = f.read()
        # Available types: PLAIN_TEXT, HTML
        type_ = enums.Document.Type.PLAIN_TEXT
        document = {"content": text_content, "type": type_}
        # Optional. If not specified, the language is automatically detected.
        # For list of supported languages:
        # https://cloud.google.com/natural-language/docs/languages
        if lang is not None:
            document["language"] = lang
        response = client.classify_text(document)
        self._write_json(json_file, response)
        return response


class ServiceVideoIntelligence(GoogleBase):
    """Class for Google Cloud Video Intelligence API

    API supports only `Google Cloud Storages`_ URIs at the moment.

    Link to `Video Intelligence PyPI`_ page.

    .. _Video Intelligence PyPI: https://pypi.org/project/google-cloud-videointelligence
    .. _Google Cloud Storages: https://cloud.google.com/storage/
    """

    __service_name = "video-intelligence"

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceVideoIntelligence init")

    @google_dependency_required
    def init_video_intelligence_client(
        self, service_credentials_file: str = None
    ) -> None:
        """Initialize Google Video Intelligence client
        """
        client = videointelligence.VideoIntelligenceServiceClient.from_service_account_json(  # noqa: E501 # pylint: disable=C0301
            service_credentials_file
        )
        self._set_service(self.__service_name, client)

    @google_dependency_required
    def annotate_video(
        self,
        video_uri: str = None,
        video_file: str = None,
        json_file: str = None,
        features: list = None,
    ):
        """Annotate video

        Possible values for features:
        - FEATURE_UNSPECIFIED, Unspecified.
        - LABEL_DETECTION, Label detection. Detect objects, such as dog or flower.
        - SHOT_CHANGE_DETECTION, Shot change detection.
        - EXPLICIT_CONTENT_DETECTION, Explicit content detection.
        - SPEECH_TRANSCRIPTION, Speech transcription.
        - TEXT_DETECTION, OCR text detection and tracking.
        - OBJECT_TRACKING, Object detection and tracking.
        - LOGO_RECOGNITION, Logo detection, tracking, and recognition.

        If `video_uri` is given then that is used even if `video_file` is None.

        :param video_uri: Google Cloud Storage URI
        :param video_file: filepath to video
        :param json_file: json target to save result, defaults to None
        :param features: list of annotation features to detect,
            defaults to ["LABEL_DETECTION", "SHOT_CHANGE_DETECTION"]
        :return: annotate result
        """
        client = self._get_client_for_service(self.__service_name)
        response = None
        if features is None:
            features = ["LABEL_DETECTION", "SHOT_CHANGE_DETECTION"]
        if video_uri:
            response = client.annotate_video(
                input_uri=video_uri, features=features
            ).result()
        elif video_file:
            with open(video_file, "rb") as f:
                response = client.annotate_video(
                    input_content=f.read(), features=features
                ).result()
        self._write_json(json_file, response)
        return response


class ServiceTranslation(GoogleBase):
    """Class for Google Cloud Translation API

    Link to `Translation PyPI`_ page.

    .. _Translation PyPI: https://pypi.org/project/google-cloud-translate/
    """

    __service_name = "translation"

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceTranslation init")
        self.__project_id = ""

    @google_dependency_required
    def init_translation_client(
        self, service_credentials_file: str, project_identifier: str
    ) -> None:
        """Initialize Google Translation client
        """
        client = translate_v3.TranslationServiceClient.from_service_account_json(  # noqa: E501 # pylint: disable=C0301
            service_credentials_file
        )
        self._set_service(self.__service_name, client)
        self.__project_id = project_identifier

    @google_dependency_required
    def translate(
        self, text: Any, source_language: str = None, target_language: str = None
    ) -> dict:
        """Translate text

        :param text: text to translate
        :param source_language: language code, defaults to None
        :param target_language: language code, defaults to None
        :return: translated text
        """
        client = self._get_client_for_service(self.__service_name)
        if not text and not target_language:
            raise KeyError("text and target_language are required parameters")
        parent = client.location_path(self.__project_id, "global")
        if isinstance(text, str):
            text = [text]
        response = client.translate_text(
            contents=text,
            source_language_code=source_language,
            target_language_code=target_language,
            parent=parent,
        )
        return response


class ServiceTextToSpeech(GoogleBase):
    """Class for Google Cloud Text-to-Speech API

    Link to `Text To Speech PyPI`_ page.

    .. _Text To Speech PyPI: https://pypi.org/project/google-cloud-texttospeech/
    """

    __service_name = "text-to-speech"

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceTextToSpeech init")

    @google_dependency_required
    def init_text_to_speech_client(self, service_credentials_file: str) -> None:
        """Initialize Google Text To Speech client
        """
        client = texttospeech_v1.TextToSpeechClient.from_service_account_json(  # noqa: E501 # pylint: disable=C0301
            service_credentials_file
        )
        self._set_service(self.__service_name, client)

    @google_dependency_required
    def list_supported_voices(self, language_code: str = None):
        """List supported voices for the speech

        :param language_code: voice languages to list, defaults to None (all)
        :return: list of supported voices
        """
        client = self._get_client_for_service(self.__service_name)
        if language_code:
            voices = client.list_voices(language_code)
        else:
            voices = client.list_voices()
        return voices.voices

    @google_dependency_required
    def synthesize_speech(
        self,
        text,
        language="en-US",
        name="en-US-Standard-B",
        gender="MALE",
        encoding="MP3",
        target_file="synthesized.mp3",
    ):
        """Synthesize speech synchronously

        :param text: input text to synthesize
        :param language: voice language, defaults to "en-US"
        :param name: voice name, defaults to "en-US-Standard-B"
        :param gender: voice gender, defaults to "MALE"
        :param encoding: result encoding type, defaults to "MP3"
        :param target_file: save synthesized output to file,
            defaults to "synthesized.mp3"
        :return: synthesized output in bytes
        """
        if not text:
            raise KeyError("text is required for kw: synthesize_speech")
        client = self._get_client_for_service(self.__service_name)
        synth_input = SynthesisInput(text=text)
        voice_selection = VoiceSelectionParams(
            language_code=language, name=name, ssml_gender=gender
        )
        audio_config = AudioConfig(audio_encoding=encoding)
        response = client.synthesize_speech(synth_input, voice_selection, audio_config)
        if target_file:
            with open(target_file, "wb") as f:
                f.write(response.audio_content)
        return response.audio_content


class ServiceSpeechToText(GoogleBase):
    """Class for Google Cloud Speech-To-Text API

    Possible input audio encodings:
        - 'AMR'
        - 'AMR_WB'
        - 'ENCODING_UNSPECIFIED'
        - 'FLAC'
        - 'LINEAR16'
        - 'MULAW'
        - 'OGG_OPUS'
        - 'SPEEX_WITH_HEADER_BYTE'

    Link to `Speech To Text PyPI`_ page.

    .. _Speech To Text PyPI: https://pypi.org/project/google-cloud-speech/
    """

    __service_name = "speech-to-text"
    if HAS_GOOGLECLOUD:
        __encodings = {
            "AMR": speech.enums.RecognitionConfig.AudioEncoding.AMR,
            "AMR_WB": speech.enums.RecognitionConfig.AudioEncoding.AMR_WB,
            "FLAC": speech.enums.RecognitionConfig.AudioEncoding.FLAC,
            "LINEAR16": speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            "MULAW": speech.enums.RecognitionConfig.AudioEncoding.MULAW,
            "OGG": speech.enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
            "SPEEX": speech.enums.RecognitionConfig.AudioEncoding.SPEEX_WITH_HEADER_BYTE,  # noqa: E501 # pylint: disable=C0301
            "UNSPECIFIED": speech.enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,  # noqa: E501 # pylint: disable=C0301
        }
    else:
        __encodings = {}

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceSpeechToText init")

    @google_dependency_required
    def init_speech_to_text_client(self, service_credentials_file: str) -> None:
        """Initialize Google Speech To Text client
        """
        client = speech.SpeechClient.from_service_account_json(  # noqa: E501 # pylint: disable=C0301
            service_credentials_file
        )
        self._set_service(self.__service_name, client)

    @google_dependency_required
    def recognize(
        self,
        audio_file_uri,
        encoding: str = "FLAC",
        language_code: str = "en_US",
        audio_channel_count=2,
    ):
        """Recognize text in the audio file

        :param audio_file_uri: Google Cloud Storage URI
        :return: recognized texts
        """
        # flac or wav, does not require encoding type
        client = self._get_client_for_service(self.__service_name)
        audio = speech.types.RecognitionAudio(  # pylint: disable=E1101
            uri=audio_file_uri
        )
        if encoding and encoding not in self.__encodings:
            encoding = self.__encodings["UNSPECIFIED"]
        config = speech.types.RecognitionConfig(  # pylint: disable=E1101
            encoding=encoding,
            language_code=language_code,
            audio_channel_count=audio_channel_count,
            use_enhanced=True,
        )
        rec = client.recognize(config=config, audio=audio)
        return rec.results


class ServiceStorage(GoogleBase):
    """Class for Google Cloud Storage API
     and Google Cloud Storage JSON API

    You will have to grant the appropriate permissions to the
    service account you are using to authenticate with
    @google-cloud/storage. The IAM page in the console is here:
    https://console.cloud.google.com/iam-admin/iam/project

    Link to `Google Storage PyPI`_ page.

    .. _Google Storage PyPI: https://pypi.org/project/google-cloud-storage/
    """

    __service_name = "storage"

    def __init__(self) -> None:
        self.services.append(self.__service_name)
        self.logger.debug("ServiceStorage init")

    @google_dependency_required
    def init_storage_client(self, service_credentials_file: str = None) -> None:
        """Initialize Google Cloud Storage client
        """
        client = storage.Client.from_service_account_json(service_credentials_file)
        self._set_service(self.__service_name, client)

    @google_dependency_required
    def create_bucket(self, bucket_name: str):
        """Create Google Cloud Storage bucket

        :param bucket_name: name as string
        :return: bucket
        """
        client = self._get_client_for_service(self.__service_name)
        bucket = client.create_bucket(bucket_name)
        return bucket

    @google_dependency_required
    def delete_bucket(self, bucket_name: str):
        """Delete Google Cloud Storage bucket

        Bucket needs to be empty before it can be deleted.

        :param bucket_name: name as string
        """
        bucket = self.get_bucket(bucket_name)
        try:
            bucket.delete()
        except Exception:
            raise ValueError("The bucket you tried to delete was not empty")

    @google_dependency_required
    def get_bucket(self, bucket_name: str):
        """Get Google Cloud Storage bucket

        :param bucket_name: name as string
        :return: bucket
        """
        if not bucket_name:
            raise KeyError("bucket_name is required for kw: get_bucket")
        client = self._get_client_for_service(self.__service_name)
        bucket = client.get_bucket(bucket_name)
        return bucket

    @google_dependency_required
    def list_buckets(self) -> list:
        """List Google Cloud Storage buckets

        :return: list of buckets
        """
        client = self._get_client_for_service(self.__service_name)
        buckets = list(client.list_buckets())
        return buckets

    @google_dependency_required
    def delete_files(self, bucket_name: str, files: Any):
        """Delete files in the bucket

        Files need to be object name in the bucket.

        :param bucket_name: name as string
        :param files: single file, list of files or
            comma separated list of files
        :return: list of files which could not be deleted,
            or True if all were deleted
        """
        if not bucket_name or not files:
            raise KeyError("bucket_name and files are required for kw: delete_files")
        if not isinstance(files, list):
            files = files.split(",")
        bucket = self.get_bucket(bucket_name)
        notfound = []
        for filename in files:
            filename = filename.strip()
            blob = bucket.get_blob(filename)
            if blob:
                blob.delete()
            else:
                notfound.append(filename)
        return notfound if len(notfound) > 0 else True

    @google_dependency_required
    def list_files(self, bucket_name: str):
        """List files in the bucket

        :param bucket_name: name as string
        :return: list of object names in the bucket
        """
        if not bucket_name:
            raise KeyError("bucket_name is required for kw: list_files")
        bucket = self.get_bucket(bucket_name)
        all_blobs = bucket.list_blobs()
        return sorted(blob.name for blob in all_blobs)

    @google_dependency_required
    def upload_file(self, bucket_name: str, filename: str, target_name: str):
        """Upload a file into a bucket

        :param bucket_name: name as string
        :param filename: filepath to upload file
        :param target_name: target object name
        """
        if not bucket_name or not filename or not target_name:
            raise KeyError(
                "bucket_name, filename and target_name are required for kw: upload_file"
            )
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(target_name)
        with open(filename, "rb") as f:
            blob.upload_from_file(f)

    @google_dependency_required
    def upload_files(self, bucket_name: str, files: dict):
        """Upload files into a bucket

        Example `files`:
        files = {"mytestimg": "image1.png", "mydoc": "google.pdf"}

        :param bucket_name: name as string
        :param files: dictionary of object names and filepaths
        """
        if not bucket_name or not files:
            raise KeyError("bucket_name and files are required for kw: upload_files")
        if not isinstance(files, dict):
            raise ValueError("files needs to be an dictionary")
        bucket = self.get_bucket(bucket_name)
        for target_name, filename in files.items():
            blob = bucket.blob(target_name)
            blob.upload_from_filename(filename)

    @google_dependency_required
    def download_files(self, bucket_name: str, files: Any):
        """Download files from a bucket

        Example `files`:
        files = {"mytestimg": "image1.png", "mydoc": "google.pdf

        :param bucket_name: name as string
        :param files: list of object names or dictionary of
            object names and target files
        :return: list of files which could not be downloaded, or
            True if all were downloaded
        """
        if isinstance(files, str):
            files = files.split(",")
        bucket = self.get_bucket(bucket_name)
        notfound = []
        if isinstance(files, dict):
            for object_name, filename in files.items():
                blob = bucket.get_blob(object_name)
                if blob:
                    with open(filename, "wb") as f:
                        blob.download_to_file(f)
                        self.logger.info(
                            "Downloaded object %s from Google to filepath %s",
                            object_name,
                            filename,
                        )
                else:
                    notfound.append(object_name)
        else:
            for filename in files:
                filename = filename.strip()
                blob = bucket.get_blob(filename)
                if blob:
                    with open(filename, "wb") as f:
                        blob.download_to_file(f)
                        self.logger.info(
                            "Downloaded object %s from Google to filepath %s",
                            filename,
                            filename,
                        )
                else:
                    notfound.append(filename)
        return notfound if len(notfound) > 0 else True


class Google(  # pylint: disable=R0901
    ServiceVision,
    ServiceNaturalLanguage,
    ServiceVideoIntelligence,
    ServiceTranslation,
    ServiceTextToSpeech,
    ServiceSpeechToText,
    ServiceStorage,
):
    """Library for interacting with Google services

    Google Storage URI:

        gs://<bucket_name>/<file_path_inside_bucket>

    The usage requires the following steps:

        - Create GCP project
        - Create service account key file (json) and save it to a place the robot
          can use it
        - Enable APIs
        - Install rpaframework[google]

    Services are taken into use with ``init_SERVICENAME_client`` keywords,
    which take as parameter an ``service_account`` JSON file.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        ServiceVision.__init__(self)
        ServiceNaturalLanguage.__init__(self)
        ServiceVideoIntelligence.__init__(self)
        ServiceTranslation.__init__(self)
        ServiceTextToSpeech.__init__(self)
        ServiceSpeechToText.__init__(self)
        ServiceStorage.__init__(self)
        self.logger.info("Google library initialized")
