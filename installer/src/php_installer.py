import os

from .b_colors import BColors


class PHPInstaller:
    def __init__(self):
        pass

    def _request_php_install(self):
        available_versions = ['7.2', '7.4', '8.0']
        print(BColors.ok_cyan + BColors.bold + f'PHP installation setup' + BColors.end_c)
        want_php = self._request_confirm('Do you want to install PHP?')
        if want_php:
            php_version = self._select_php_version(available_versions)
            os.system('apt install software-properties-common -y')
            os.system('add-apt-repository ppa:ondrej/php -y')
            os.system('apt update')
            os.system(
                f'apt install php{php_version} '
                f'php{php_version}-{{fpm, bz2,bcmath,curl,intl,readline,xml,zip,fpm,gd,mbstring}} -y'
            )
            print(BColors.ok_green + 'PHP installed correctly' + BColors.end_c)
        return True

    def _select_php_version(self, all_versions):
        php_list = ''
        i = 1
        for v in all_versions:
            php_list += f'{i}) {v}\n'
            i += 1
        php_version_select = self._request_int_input(f'Select the PHP Version you want to install it:\n\n{php_list}')
        if 0 < int(php_version_select) <= len(all_versions):
            return all_versions[int(php_version_select) - 1]
        return self._select_php_version(all_versions)

    # noinspection PyBroadException
    def _request_int_input(self, message):
        value = input(message)
        try:
            return int(value)
        except Exception:
            return self._request_int_input(message)
