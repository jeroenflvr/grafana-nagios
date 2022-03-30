import attr
import itertools
from attr.validators import instance_of
from numbers import Number
from grafanalib.validators import is_interval, is_in, is_color_code, is_list_of
from grafanalib.core import (
    RGBA, Percent, Pixels, DashboardLink,
    DEFAULT_ROW_HEIGHT, BLANK, GREEN)


@attr.s
class NagiosTarget(object):
    """Generates Nagios datasource target JSON structure.


    :param host: hostname
    :param perflabel: label in nagios perf_data
    :param service: name of the nagios check
    :param graphtype: type, default is AVERAGE 
    :factor: multiplication factor for values
    """

    fill = attr.ib(default="fill", validator=instance_of(str))
    host = attr.ib(default="", validator=instance_of(str))
    perflabel = attr.ib(default="", validator=instance_of(str))
    service = attr.ib(default="", validator=instance_of(str))
    refId = attr.ib(default="A", validator=instance_of(str))
    graphtype = attr.ib(default="AVERAGE", validator=instance_of(str))
    factor = attr.ib(default="")

    def to_json_data(self):
        obj = {
            'host': self.host,
            'fill': self.fill,
            'perflabel': self.perflabel,
            'service': self.service,
            'refId': self.refId,
            'type': self.graphtype,
            'factor': self.factor,
        }
        return obj


