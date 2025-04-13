import logging
import subprocess
import distutils.spawn
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

logger = logging.getLogger(__name__)


def get_active_session_id(user: str) -> str | None:
    """
    Returns the session ID of the active session for the given user.
    If no active session is found, returns None.
    """
    try:
        sessions = subprocess.check_output(['loginctl', 'list-sessions'], text=True).splitlines()
        for line in sessions[1:]:  # Skip header
            columns = line.split()
            if len(columns) >= 5 and columns[2] == user and 'active' in line:
                return columns[0]
    except subprocess.CalledProcessError as e:
        logger.info(f"Error retrieving sessions: {e}")
    return None

class SystemManagementDirect(Extension):
  def __init__(self):
    logger.info('Loading Gnome Settings Extension')
    super(SystemManagementDirect, self).__init__()
    self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):
  def on_event(self, event, extension):
    keyword = event.get_keyword()

    # Find the keyword id using the keyword (since the keyword can be changed by users)
    for id, kw in extension.preferences.items():
      if kw == keyword:
        self.on_match(id)
        return HideWindowAction()

  def on_match(self, id):
    if id == 'lock-screen':
      subprocess.Popen(['loginctl', 'lock-session'])
    if id == 'suspend':
      subprocess.Popen(['systemctl', 'suspend', '-i'])
    if id == 'shutdown':
      subprocess.Popen(['systemctl', 'poweroff', '-i'])
    if id == 'restart':
      subprocess.Popen(['systemctl', 'reboot', '-i'])
    if id == 'logout':
        session_id = get_active_session_id()
        if session_id:
            subprocess.run(['loginctl', 'terminate-session', session_id], check=True)
            logger.info(f"Terminated session {session_id}.")
        else:
            logger.info("No active session found for current user.")


SystemManagementDirect().run()
