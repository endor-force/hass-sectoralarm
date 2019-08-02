""" Simple asynchronous package for interacting with Sector Alarms web panel """

from .util import get_json


class AsyncSector(object):
    """ Class to interact with sector alarm web panel """

    Base = 'https://mypagesapi.sectoralarm.net/'
    Login = 'User/Login'
    Alarm = 'Panel/GetOverview'
    Temperatures = 'Panel/GetTempratures/'
    History = 'Panel/GetPanelHistory/{}'
    Arm = 'Panel/ArmPanel'
    Version = 'v1_1_68'

    @classmethod
    async def create(cls, session, alarm_id, username, password):
        """ factory """
        self = AsyncSector(session, alarm_id, username, password)
        logged_in = await self.login()

        return self if logged_in else None

    def __init__(self, session, alarm_id, username, password):
        self.alarm_id = alarm_id
        self._session = session
        self._auth = {'userID': username, 'password': password}

    async def login(self):
        """ Tries to Login to Sector Alarm """

        response = await self._session.post(
            AsyncSector.Base + AsyncSector.Login, json=self._auth)

        if response.status == 200:
            result = await response.text()
            if 'frmLogin' in result:
                return False
            return True

        return False

    async def get_status(self):
        """
        Fetches the status of the alarm
        """
        request = self._session.post(
            AsyncSector.Base + AsyncSector.Alarm,
            data={
                'PanelId': self.alarm_id,
                'Version': AsyncSector.Version
            }
        )

        return await get_json(request)

    async def get_temperatures(self):
        """
        Fetches a list of all temperature sensors
        """
        data = {
            'id': self.alarm_id,
            'Version': AsyncSector.Version
        }
        request = self._session.post(
            AsyncSector.Base + AsyncSector.Temperatures,
            json=data)


        return await get_json(request)

    async def get_history(self):
        """
        Fetches the alarm event log/history
        """
        request = self._session.get(AsyncSector.Base +
                                    AsyncSector.History.format(self.alarm_id))

        return await get_json(request)

    async def alarm_toggle(self, state, code=None):
        """
        Tries to toggle the state of the alarm
        """
        data = {
            'ArmCmd': state,
            'PanelCode': code,
            'HasLocks': False,
            'id': self.alarm_id
        }

        request = self._session.post(
            AsyncSector.Base + AsyncSector.Arm, json=data)

        result = await get_json(request)
        if 'status' in result and result['status'] == 'success':
            return True

        return False

    async def disarm(self, code=None):
        """ Send disarm command """
        return await self.alarm_toggle('Disarm', code=code)

    async def arm_home(self, code=None):
        """ Send arm home command """
        return await self.alarm_toggle('Partial', code=code)

    async def arm_away(self, code=None):
        """ Send arm away command """
        return await self.alarm_toggle('Total', code=code)
