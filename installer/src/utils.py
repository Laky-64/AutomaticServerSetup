import os
import re
import subprocess
from os.path import isfile

from .b_colors import BColors
import sys


class Utils:

    @staticmethod
    def _is_windows() -> bool:
        return sys.platform.startswith('win')

    @staticmethod
    def _get_os_full_desc():
        name = ''
        if isfile('/etc/lsb-release'):
            lines = open('/etc/lsb-release').read().split('\n')
            for line in lines:
                if line.startswith('DISTRIB_DESCRIPTION='):
                    name = line.split('=')[1]
                    if name[0] == '"' and name[-1] == '"':
                        return name[1:-1]
        if isfile('/suse/etc/SuSE-release'):
            return open('/suse/etc/SuSE-release').read().split('\n')[0]
        try:
            # noinspection PyUnresolvedReferences
            import platform
            return ' '.join(platform.dist()).strip().title()
        except ImportError:
            pass
        if os.name == 'posix':
            os_type = os.getenv('OSTYPE')
            if os_type != '':
                return os_type
        return os.name

    @staticmethod
    def _str_in_array(query: str, list_check: list):
        for item in list_check:
            if item.upper() in query.upper():
                return True
        return False

    def _is_supported_linux_os(self):
        supported_os_list = [
            'Ubuntu'
        ]
        return self._str_in_array(self._get_os_full_desc(), supported_os_list)

    def _std_err(self, message: str):
        print(('Error: ' if self._is_windows() else BColors.fail + 'Error: ' + BColors.end_c) + message)

    def _request_confirm(self, message: str):
        try:
            result = input(message + ' (Y/N)\n')
            if result.upper() == 'Y' or result.upper() == 'N':
                return result.upper() == 'Y'
            else:
                return self._request_confirm(message)
        except KeyboardInterrupt:
            pass

    @staticmethod
    def _get_version(package_check):
        # noinspection PyBroadException
        try:
            result_cmd = subprocess.Popen(
                [package_check, '-v'],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            ).communicate()
            result_cmd = result_cmd[0].decode() if len(result_cmd[0].decode()) > 0 else result_cmd[1].decode()
        except Exception:
            return {
                'version_info': {},
                'version': '0',
            }
        print(result_cmd)
        version = re.search('(\d+\.?)+$', result_cmd).group(0)
        return {
            'version_info': {
                'major': int(version.split('.')[0]),
                'minor': int(version.split('.')[1]),
            },
            'version': version,
        }
