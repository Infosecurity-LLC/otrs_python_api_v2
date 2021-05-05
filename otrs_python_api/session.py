import os
import time

from otrs_python_api.exceptions import InvalidInitArgument, InvalidSessionCacheFile


class Session:
    def __init__(self, session_cache_filename: str, read_timeout: float, login: str = None, session_id: str = None,
                 time_created: int = None, expiry: int = None):
        """
        Stores and caches session data
        :param session_cache_filename: session cache filename
        :param read_timeout: Used to determine session expiration
        :param login: Used to create a cache file
        :param session_id: Session id
        :param time_created: Session creation time
        :param expiry: Session timeout
        """
        self._session_cache_filename = session_cache_filename or f"/tmp/.otrs-sessid/{login}"
        self._read_timeout = read_timeout
        self._session_id = session_id
        self._time_created = time_created
        self._expiry = expiry or 28800
        self.validate_args()

    def validate_args(self):
        if not isinstance(self._session_cache_filename, str):
            raise InvalidInitArgument(f"Session cache file {self._session_cache_filename} must be str")
        if not isinstance(self._read_timeout, float):
            raise InvalidInitArgument(f"Read timeout {self._read_timeout} must be float")
        if self._session_id and not isinstance(self._session_id, str):
            raise InvalidInitArgument(f"Session cache file {self._session_id} must be str")
        if self._time_created and not isinstance(self._time_created, int):
            raise InvalidInitArgument(f"Read timeout {self._time_created} must be int")

    def _read_session_from_cache(self) -> (int, str):
        if not os.path.exists(self._session_cache_filename):
            self._create_cache_file()
            return None
        if os.stat(self._session_cache_filename).st_size == 0:
            return None
        with open(self._session_cache_filename) as f:
            prepared_session = f.read()
            try:
                time_created, session_id = prepared_session.split(':')
            except ValueError:
                self.clear_session()
                raise InvalidSessionCacheFile(f"Session cache filename {self._session_cache_filename} cleared")
        return session_id, int(time_created)

    def _write_session_to_file(self, session_id: str, time_created: int):
        with open(self._session_cache_filename, 'w') as f:
            f.write(str(time_created) + ':' + session_id)

    def _create_cache_file(self):
        os.makedirs(os.path.dirname(self._session_cache_filename), exist_ok=True)

    def _clear_cache_file(self):
        open(self._session_cache_filename, 'w').close()

    def _set_session_from_cache(self) -> bool:
        session_from_cache = self._read_session_from_cache()
        if not session_from_cache:
            self._session_id, self._time_created = None, None
            return False
        self._session_id, self._time_created = session_from_cache
        return True

    def get_expiry_age(self):
        """
        Get the number of seconds until the session expires. If the session is not full in the class, get from the
        cache. If the cache is empty return None
        """
        if not self._session_id or not self._time_created:
            if not self._set_session_from_cache():
                return None
        time_diff = int(time.time()) - self._time_created
        expiry_age = self._expiry - time_diff
        return expiry_age

    def get_session(self):
        """
        If the session is not full in the class, get from the cache. Check if the session has expired. If the cache is
        empty or the session has expired return None
        """
        if not self._session_id or not self._time_created:
            if not self._set_session_from_cache():
                return None

        expiry_age = self.get_expiry_age()
        if not expiry_age:
            self._session_id, self._time_created = None, None
            return None
        if expiry_age < self._read_timeout:
            self._session_id, self._time_created = None, None
            return None
        return self._session_id

    def clear_session(self):
        self._clear_cache_file()
        self._session_id, self._time_created = None, None

    def set_session(self, session_id: str):
        time_created = int(time.time())
        self._write_session_to_file(session_id, time_created)
        self._session_id = session_id
        self._time_created = time_created
