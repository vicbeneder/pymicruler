import configparser
from pkg_resources import resource_filename

config = configparser.ConfigParser()
config.read(resource_filename('pymicruler', 'config/pymicruler.ini'))


def config_resource(resource_key):
    return resource_filename('pymicruler', config['Resources'][resource_key])


def config_output(resource_key):
    return resource_filename('pymicruler', config['Output'][resource_key])


