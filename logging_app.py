
import sys
import logbook
from logbook import Logger, StreamHandler

if False :
    logging = logbook.NestedSetup([
        logbook.NullHandler(level=logbook.DEBUG),
        logbook.StreamHandler(sys.stdout, level=logbook.INFO),
        logbook.StreamHandler(sys.stderr, level=logbook.ERROR),
    ])
    logging.push_application()
    log = Logger('Logbook')
    log.info('hello, world')

if False :
    StreamHandler(sys.stdout).push_application();
    log = Logger('My Awesome Logger')
    log.info("hello")

if True :
    # handler = logbook.StderrHandler(level=level)
    # handler.formatter.format_string = '{record.time:%Y-%m-%d %H:%M:%S}|{record.level_name}|{record.message}'
    handler = logbook.StreamHandler(sys.stdout, level=logbook.INFO)
    handler.formatter.format_string = '{record.time}|{record.level_name}|{record.filename}|{record.module}|{record.func_name}|{record.lineno}|{record.message}'
    # handler.push_application()

    from sample_api import api_func;

    if False :
        log.info("hello, world")
        log.warn("hello, world")
        log.error("hello, world")
        log.critical("hello, world")


    # log.info("api func return : %d"%api_func())
    with handler.applicationbound():
        log = Logger("logging_app.py")
        log.info("hello, world")
        log.info("api func return : %d"%api_func())

if False :
    from sample_api import api_func, setup_logging
    setup_logging()

    log = Logger("logging_app.py")
    log.info("hello, world")
    log.info("api func return : %d"%api_func())

    pass
