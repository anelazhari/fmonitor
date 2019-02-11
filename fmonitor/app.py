"""smonitor: monitor list of urls for health and content

Periodically sends http request to a list of urls from config file,
logs the result and elapsed time to standart output.
It could also verify the existance of specific content in the url response
"""

import time
import threading
import queue
import logging
import requests
from requests.exceptions import RequestException, HTTPError
from fmonitor.utils import (
    parse_settings,
    validate_settings
)

# Setup logging
FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT)
_logger = logging.getLogger('__name__')
_logger.setLevel(logging.INFO)


queue = queue.Queue()
threads = []


def log_result(url, elapsed=None, success=True, failure_reason=""):
    """Log results to standard output"""
    _logger.info(
        'URL: %s, Time (s): %s, Result: %s, Reason: %s',
        url,
        elapsed,
        'Success' if success else 'Failure',
        failure_reason
    )


def process_url(item):
    """Make HTTP GET request for URL and logs the result

    Makes a HTTP GET request to URL and then saves the 
    request total elapsed time. Then itchecks if condition
    content exists in the response body. Finally, logs the
    result via the log_result function.

    Args:
        item: dictionary holding url and optionally a condition
    """
    try:
        result = requests.get(item['url'], timeout=10)
        elapsed = result.elapsed.total_seconds()
        if result.status_code != 200:
            raise HTTPError("URL Not Found")
    except RequestException as exp:
        log_result(item['url'], success=False, failure_reason="RequestException")
        _logger.debug('%s', exp)
        return

    if 'condition' in item and item['condition'] not in result.text:
        # Content is not found in result
        log_result(
            item['url'],
            elapsed=elapsed,
            success=False,
            failure_reason="ConditionNotMet"
        )
        return

    # Success result
    log_result(item['url'], elapsed=elapsed)


def worker():
    """Waits for urls in queue then process them

    This function is to be used as a thread, it waits
    indefinitely for the queue to have tasks and then
    process them. breaks while loop if it revceives
    a None task from the queue thus closing the thread
    """
    while True:
        item = queue.get()
        if item is None:
            _logger.info('Thread is shutdown.')
            break
        process_url(item)
        queue.task_done()


def main():
    """Spawns worker threads and then starts main loop

    Spawns number of worker threads as defined in settings file,
    then start main infinite loop where it sleeps for an interval
    also defined in settings file and then loads urls to process in
    the queue

    Use Ctl-C to interrupt the loop and then it will send task for the
    workers to exist.
    """

    # Parse and test the settings file
    settings = parse_settings()
    if not settings:
        return
    if not validate_settings(settings):
        return

    # Starting worker threads
    num_workers = settings.get('workers', 5)
    _logger.info("Starting %s worker threads.", num_workers)
    for _ in range(num_workers):
        worker_thread = threading.Thread(target=worker)
        worker_thread.start()
        threads.append(worker_thread)

    # Main loop
    try:
        _logger.info("Main loop started.")
        while True:
            for task in settings['urls']:
                queue.put(task)
            # Suspend execution for interval (Free the CPU)
            time.sleep(settings.get('interval', 5))
    except KeyboardInterrupt:
        _logger.info("Stopping workers...")
        for _ in range(num_workers):
            queue.put(None)
        for worker_thread in threads:
            worker_thread.join()

