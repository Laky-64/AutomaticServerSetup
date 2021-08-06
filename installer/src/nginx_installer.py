import os
import re
import socket
import subprocess

import requests as requests

from .b_colors import BColors


class NginxInstaller:
    def __init__(self):
        pass

    @staticmethod
    def _get_online_version() -> str:
        html = requests.get('https://nginx.org/en/download.html').text
        html = re.search('download/nginx-(.*?)"', html).group(0).replace('.tar.gz"', '').replace('download/', '')
        return re.search('(\d+\.?)+$', html).group(0)

    def _request_nginx_install(self):
        online_version = self._get_online_version()
        print(BColors.ok_cyan + BColors.bold + f'Nginx v.{online_version} installation setup' + BColors.end_c)
        want_nginx = self._request_confirm('Do you want to install Nginx?')
        if want_nginx:
            nginx_info = self._get_version('nginx')
            if len(nginx_info['version_info']) > 0:
                is_new = False
                is_clean = self._request_confirm('Do you want to do a clean upgrade?')
            elif os.path.exists('/etc/nginx/'):
                is_new = True
                is_clean = self._request_confirm('Do you want to do a clean installation?')
            else:
                is_new = True
                is_clean = False
            os_name = self._get_os_full_desc()
            if 'Ubuntu' in os_name:
                self._ubuntu_install(nginx_info, is_new, is_clean)
            else:
                print(BColors.fail + 'Nginx not installed' + BColors.end_c)
                return False
            print(BColors.ok_green + 'Nginx installed correctly' + BColors.end_c)
            self._run_configuration()
            print(BColors.ok_green + 'Nginx configured correctly' + BColors.end_c)
        return True

    @staticmethod
    def _ubuntu_install(nginx_info, is_new, is_clean):
        if not is_new:
            print(BColors.fail + f'Uninstalling Nginx v.{nginx_info["version"]}...' + BColors.end_c)
            os.system('apt purge nginx* -y')
            os.system('apt autoremove -y')

        if is_clean and os.path.exists('/etc/nginx/'):
            print(BColors.fail + f'Clearing Files...' + BColors.end_c)
            os.system('rm -r /etc/nginx/')

        print('Installing Curl & Certificates...')
        os.system('sudo apt install curl gnupg2 ca-certificates lsb-release -y')
        print('Adding APT Package...')
        os.system(
            'echo "deb http://nginx.org/packages/mainline/ubuntu `lsb_release -cs` nginx" \
            | sudo tee /etc/apt/sources.list.d/nginx.list'
        )
        print('Setting up Priority package...')
        os.system(
            'echo "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900\n" \
            | sudo tee /etc/apt/preferences.d/99nginx'
        )
        print('Importing signing key...')
        os.system('curl -o /tmp/nginx_signing.key https://nginx.org/keys/nginx_signing.key')
        print('Adding key to the apt trusted storage...')
        os.system('mv /tmp/nginx_signing.key /etc/apt/trusted.gpg.d/nginx_signing.asc')
        os.system('apt update')
        os.system('apt install nginx -y')

    @staticmethod
    def _check_port(port: int):
        location = ("127.0.0.1", port)
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result_of_check = a_socket.connect_ex(location)
        a_socket.close()
        return result_of_check == 0

    # noinspection PyBroadException
    def _request_int_input(self, message):
        value = input(message)
        try:
            return int(value)
        except Exception:
            return self._request_int_input(message)

    def _check_port_test(self, protocol):
        port = self._request_int_input(f"Your {protocol} listen port\n")
        if not self._check_port(port):
            return port
        else:
            print(BColors.fail + 'Port already in use!' + BColors.end_c)
            return self._check_port_test(protocol)

    # noinspection PyBroadException
    def _check_folder(self):
        folder = input("What root folder do you want?\n")
        if folder.lower() == 'default':
            try:
                os.mkdir('/var/www')
            except Exception:
                pass
            try:
                os.mkdir('/var/www/html')
            except Exception:
                pass
            return '/var/www/html'
        if os.path.exists(folder):
            return folder
        else:
            print(os.path.exists(folder))
            print(folder)
            print(BColors.fail + 'Invalid path!' + BColors.end_c)
            return self._check_folder()

    # noinspection PyBroadException
    def _check_cert(self):
        folder = input("Write your SSL Certificate path here\n")
        if os.path.exists(folder) and os.path.isfile(folder):
            return folder
        else:
            print(os.path.exists(folder))
            print(folder)
            print(BColors.fail + 'Invalid path!' + BColors.end_c)
            return self._check_folder()

    # noinspection PyBroadException
    def _check_key(self):
        folder = input("Write your KEY Certificate path here\n")
        if os.path.exists(folder) and os.path.isfile(folder):
            return folder
        else:
            print(os.path.exists(folder))
            print(folder)
            print(BColors.fail + 'Invalid path!' + BColors.end_c)
            return self._check_folder()

    @staticmethod
    def _get_php_version():
        # noinspection PyBroadException
        try:
            result_cmd = subprocess.Popen(
                ['php', '-v'],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            ).communicate()
            result_cmd = result_cmd[0].decode() if len(result_cmd[0].decode()) > 0 else result_cmd[1].decode()
        except Exception:
            return None
        return re.search('[0-9]\.[0-9]', result_cmd).group(0)

    @staticmethod
    def _save_conf(name_file, text):
        f = open(name_file, "w")
        f.write(text)
        f.close()

    @staticmethod
    def _read_conf(name_file):
        f = open(name_file, "r")
        return f.read()

    def _save_config_file(
            self,
            have_domain,
            folder,
            php_ver,
            have_https=False,
            ssl_certificate=None,
            key_certificate=None,
            with_http_redirect=False,
            domain_name=None
    ):
        default_conf = ''
        if with_http_redirect and have_domain and have_https:
            default_conf += 'server {\n'
            default_conf += f'     listen {self._check_port_test("http")};\n'
            default_conf += f'     server_name {domain_name};\n'
            default_conf += f'     return 302 https://$server_name$request_uri;\n'
            default_conf += '}'
        default_conf += 'server {\n'
        if not (with_http_redirect and have_domain and have_https):
            default_conf += f'     listen {self._check_port_test("http")};\n'
        else:
            default_conf += f'     listen {self._check_port_test("https")} ssl http2;\n'
        if have_https:
            default_conf += f'     ssl_certificate {ssl_certificate};\n'
            default_conf += f'     ssl_certificate_key {key_certificate};\n'
        if have_domain:
            default_conf += f'     server_name {domain_name};\n'
        default_conf += f'     root {folder};\n'
        default_conf += '     index index.php;\n'
        default_conf += '     location / {\n'
        default_conf += '         try_files $uri $uri/ = 404;\n'
        default_conf += '     }\n'
        if php_ver is not None:
            default_conf += '     location ~ \.php$ {\n'
            default_conf += '         include snippets/fastcgi-php.conf;\n'
            default_conf += f'         fastcgi_pass unix:/run/php/php{php_ver}-fpm.sock;\n'
            default_conf += '     }\n'
        default_conf += '     location ^~ /log/ {\n'
        default_conf += '         deny all;\n'
        default_conf += '         return 404;\n'
        default_conf += '     }\n'
        # noinspection PyBroadException
        try:
            os.mkdir(f'{folder}/log')
        except Exception:
            pass
        default_conf += f'     access_log {folder}/log/access.log;\n'
        default_conf += f'     error_log {folder}/log/error.log;\n'
        default_conf += '}'
        name_file = 'default' if not have_domain else domain_name
        self._save_conf(f'/etc/nginx/conf.d/{name_file}.conf', default_conf)
        os.system(f'chown -R www-data:www-data {folder}')

    def _make_config_files(self):
        php_ver = self._get_php_version()
        have_domain = self._request_confirm('Do you have Server Name?')
        folder = self._check_folder()
        if have_domain:
            host_name = input('Write your Server Name\n').replace('https://', '').replace('http://', '') \
                .replace('/', '')
            have_https = self._request_confirm('Do you have HTTPS?')
            if have_https:
                http_redirect = self._request_confirm('Do you want redirect from HTTP to HTTPS?')
                cert_file = self._check_cert()
                key_file = self._check_key()
                self._save_config_file(
                    have_domain, folder, php_ver, have_https, cert_file, key_file, http_redirect, host_name
                )
            else:
                self._save_config_file(have_domain, folder, php_ver, have_https, None, None, False, host_name)
        else:
            self._save_config_file(have_domain, folder, php_ver)
        another_domain = self._request_confirm('Do you want to register another domain?')
        if another_domain:
            self._make_config_files()

    def _run_configuration(self):
        self._make_config_files()
        nginx_conf_path = '/etc/nginx/nginx.conf'
        self._save_conf(nginx_conf_path, self._read_conf(nginx_conf_path).replace('user  nginx;', 'user  www-data;'))
        # noinspection PyBroadException
        try:
            os.mkdir('/etc/nginx/snippets')
        except Exception:
            pass
        fastcgi = 'fastcgi_split_path_info ^(.+\.php)(/.+)$;\n'
        fastcgi += 'try_files $fastcgi_script_name = 404;\n'
        fastcgi += 'set $path_info $fastcgi_path_info;\n'
        fastcgi += 'fastcgi_param PATH_INFO $path_info;\n'
        fastcgi += 'fastcgi_index index.php;\n'
        fastcgi += 'include fastcgi.conf;'
        self._save_conf('/etc/nginx/snippets/fastcgi-php.conf', fastcgi)
        fastcgi_conf = 'fastcgi_param  SCRIPT_FILENAME    $document_root$fastcgi_script_name;\n'
        fastcgi_conf += 'fastcgi_param  QUERY_STRING       $query_string;\n'
        fastcgi_conf += 'fastcgi_param  REQUEST_METHOD     $request_method;\n'
        fastcgi_conf += 'fastcgi_param  CONTENT_TYPE       $content_type;\n'
        fastcgi_conf += 'fastcgi_param  CONTENT_LENGTH     $content_length;\n\n'
        fastcgi_conf += 'fastcgi_param  SCRIPT_NAME        $fastcgi_script_name;\n'
        fastcgi_conf += 'fastcgi_param  REQUEST_URI        $request_uri;\n'
        fastcgi_conf += 'fastcgi_param  DOCUMENT_URI       $document_uri;\n'
        fastcgi_conf += 'fastcgi_param  DOCUMENT_ROOT      $document_root;\n'
        fastcgi_conf += 'fastcgi_param  SERVER_PROTOCOL    $server_protocol;\n'
        fastcgi_conf += 'fastcgi_param  REQUEST_SCHEME     $scheme;\n'
        fastcgi_conf += 'fastcgi_param  HTTPS              $https if_not_empty;\n\n'
        fastcgi_conf += 'fastcgi_param  GATEWAY_INTERFACE  CGI/1.1;\n'
        fastcgi_conf += 'fastcgi_param  SERVER_SOFTWARE    nginx/$nginx_version;\n\n'
        fastcgi_conf += 'fastcgi_param  REMOTE_ADDR        $remote_addr;\n'
        fastcgi_conf += 'fastcgi_param  REMOTE_PORT        $remote_port;\n'
        fastcgi_conf += 'fastcgi_param  SERVER_ADDR        $server_addr;\n'
        fastcgi_conf += 'fastcgi_param  SERVER_PORT        $server_port;\n'
        fastcgi_conf += 'fastcgi_param  SERVER_NAME        $server_name;\n\n'
        fastcgi_conf += 'fastcgi_param  REDIRECT_STATUS    200;\n'
        self._save_conf('/etc/nginx/fastcgi.conf', fastcgi_conf)
        os.system('service nginx restart')
