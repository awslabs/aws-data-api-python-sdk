class Credentials:
    access_key = None
    secret_key = None
    session_token = None

    def __init__(self, access_key: str, secret_key: str, session_token: str = None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.session_token = session_token
