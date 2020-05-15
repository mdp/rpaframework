import json
from google.auth import jwt, default
from googleapiclient.discovery import build
import logging

# from pathlib import Path
# from typing import Any

from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError
from RPA.RobotLogListener import RobotLogListener

# from RPA.core.utils import required_param, required_env

# from RPA.Tables import Tables

try:
    BuiltIn().import_library("RPA.RobotLogListener")
except RobotNotRunningError:
    pass

DEFAULT_REGION = "eu-west-1"


class GoogleBase:
    """Google base class for generic methods"""

    logger = None
    services: list = []
    clients: dict = {}
    region: str = None


class Google:
    """Library for interacting with Google services

    Supported services:
        -

    Todo:
        - vision (Cloud Vision API) https://pypi.org/project/google-cloud-vision/
        - video (Cloud Video Intelligence API) https://pypi.org/project/google-cloud-videointelligence
        - natural_language (Cloud Natural Language API) https://pypi.org/project/google-cloud-language/
        - translation (Cloud Translation API) https://pypi.org/project/google-cloud-translate/
        - text_to_speech (Cloud Text-to-Speech API) https://pypi.org/project/google-cloud-texttospeech/
        - speech_to_text (Cloud Speech-to-Text API) https://pypi.org/project/google-cloud-speech/

    Later:
        - search
            - all
            - images
            - maps
            - videos
            - news
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # listener = RobotLogListener()
        # listener.register_protected_keywords(
        #     [f"init_{s}_client" for s in self.services]
        # )
        # listener.only_info_level(["list_files"])
        self.logger.info("Google library initialized")


if __name__ == "__main__":
    import pprint

    library = Google()
    # customsearch = build(
    #     "customsearch", "v1", developerKey="AIzaSyBjxpBnk-_aqVur_PlpuA2_60rhpnIyqDc"
    # )
    # res = customsearch.cse().list(q="rpaframework").execute()
    # pprint.pprint(res)

    with open("/Users/mika/koodi/auth.json", "r") as fh:
        info = json.load(fh)
    credentials = jwt.Credentials.from_service_account_info(info, audience="audience")
    credentials.refresh(None)
    print(credentials.valid)
    print(credentials.expired)
    print(credentials.token)
    print(dir(credentials))

    # credentials, project_id = default()
    vision_service = build("vision", "v1", credentials=credentials)
    print(vision_service)
    print(dir(vision_service))


"""
https://developers.google.com/apis-explorer?authuser=1


Google Custom Search enables you to create a search engine for your website, your blog, or a collection of websites
https://rayxyz.github.io/tech/2018/05/16/setup-google-custom-search-and-search-images-using-python.html

google-api-python-client
  - Installing pyasn1 (0.4.8)
  - Installing cachetools (4.1.0)
  - Installing protobuf (3.11.3)
  - Installing pyasn1-modules (0.2.8)
  - Updating python-dateutil (2.8.1 /Users/mika/.local/lib/python3.7/site-packages -> 2.8.1)
  - Installing rsa (4.0)
  - Installing google-auth (1.14.3)
  - Installing googleapis-common-protos (1.51.0)
  - Installing httplib2 (0.17.3)
  - Updating oauthlib (3.1.0 /Users/mika/.local/lib/python3.7/site-packages -> 3.1.0)
  - Updating dnspython (1.16.0 /Users/mika/.local/lib/python3.7/site-packages -> 1.16.0)
  - Installing google-api-core (1.17.0)
  - Installing google-auth-httplib2 (0.0.3)
  - Updating requests-oauthlib (1.3.0 /Users/mika/.local/lib/python3.7/site-packages -> 1.3.0)
  - Installing uritemplate (3.0.1)
  - Updating xlrd (1.2.0 /Users/mika/.local/lib/python3.7/site-packages -> 1.2.0)
  - Installing google-api-python-client (1.8.3)

 """
