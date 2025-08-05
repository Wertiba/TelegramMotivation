import uuid
import os

from dotenv import load_dotenv, find_dotenv
from google_auth_oauthlib.flow import Flow
from src.services.google_integration.settings import SCOPES, REDIRECT_URI, CREDS_PATH
from src.services.DB.storage import Storage
from src.services.singleton import singleton
from src.services.DB.database_config import charset, port

@singleton
class Authentication:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.storage = Storage(os.getenv('DB_HOST'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'), os.getenv('DB_NAME'), charset, port=port)


    def get_auth_url(self, user_tgid):
        state = str(uuid.uuid4())
        self.storage.set_state(user_tgid, state)

        flow = Flow.from_client_secrets_file(
            CREDS_PATH,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        auth_url, _ = flow.authorization_url(state=state, access_type='offline', include_granted_scopes='true')
        return auth_url

    def retrieve_user_by_state(self, state):
        try:
            return self.storage.get_tgid_by_state(state)[0]
        except Exception:
            return False
