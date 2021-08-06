import os

from .src import Src
from .src.b_colors import BColors


class Setup(Src):
    def run(self):
        user = os.getenv("SUDO_USER")
        if user is None:
            print(BColors.fail + 'Root User Needed!' + BColors.end_c)
            os.system('sudo su')
        if self._is_windows():
            self._std_err('Installation not Supported on Windows')
        elif self._is_supported_linux_os():
            self._request_php_install()
            self._request_nginx_install()
        else:
            self._std_err('This Linux distro is not Supported')
