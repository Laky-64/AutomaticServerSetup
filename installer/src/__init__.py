from .php_installer import PHPInstaller
from .nginx_installer import NginxInstaller
from .utils import Utils


class Src(PHPInstaller, NginxInstaller, Utils):
    pass
