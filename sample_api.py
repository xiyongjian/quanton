
import logbook
import sys
from logbook import Logger

def setup_logging() :
    handler = logbook.StreamHandler(sys.stdout, level=logbook.INFO)
    handler.formatter.format_string = '{record.time}|{record.level_name}|{record.module}|{record.func_name}|{record.lineno}|{record.message}'
    handler.push_application()

log = Logger("simple_api")

def api_func() :
    log.info("return 999")
    return 999