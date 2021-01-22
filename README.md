# Crawler (development version)

### Usage example
python3 run_crawler.py seed_targets_list.txt

### seed_targets_list
Example:
> https://en.wikipedia.org/wiki/Machine_learning

### Options
python3 run_crawler.py --help
Option examples:
```
positional arguments:
  SEED_TARGETS_LIST     A file containing seed URLs one in each line (Example:
                        ./seed_targets_list.txt)

optional arguments:
  -h, --help            show this help message and exit
  --log_folder LOG_FOLDER
                        Folder path for logs (Default: log)
  --log_save_every_second LOG_SAVE_EVERY_SECOND
                        Interval of saving logs to disk (Default: 30)
  --log_show_log_level LOG_SHOW_LOG_LEVEL
                        0: Show all logs, 1: Show only Info and FATAL, 2: Show
                        only FATAL, 3: Show progress bar (Default: 3)
  --max_number_of_crawlers MAX_NUMBER_OF_CRAWLERS
                        Number of multi-threaded crawlers (Default: 8)
  --max_number_of_doc_parsers MAX_NUMBER_OF_DOC_PARSERS
                        Number of multi-threaded document parsers (Default: 8)
  --storage_folder STORAGE_FOLDER
                        Folder path for storage (Default: ./storage)
  --storage_num_doc_limit STORAGE_NUM_DOC_LIMIT
                        Storage limit in number of files, above which the
                        crawlers stop (Default: 100000)
  --storage_size_limit_mb STORAGE_SIZE_LIMIT_MB
                        Storage limit in MB, above which the crawlers stop
                        (Default: 300)
  --url_allowed_domain URL_ALLOWED_DOMAIN [URL_ALLOWED_DOMAIN ...]
                        A list of domain allowable, separated by space
                        (Default: en.wikipedia.org)
  --url_max_depth URL_MAX_DEPTH
                        Maximum allowable depth relative to seed (Default: 50)
  --url_max_length URL_MAX_LENGTH
                        Maximum allowable number of characters in the URL
                        (Default: 200)
  --url_max_num_slashes URL_MAX_NUM_SLASHES
                        Maximum allowable number of slashes in the URL
                        (Default: 50)
  --url_pattern URL_PATTERN
                        URL pattern in regular expression (Default:
                        https?://.*\..*/?.*)
  --url_retry_http_codes URL_RETRY_HTTP_CODES [URL_RETRY_HTTP_CODES ...]
                        HTTP Error Code that is retry-able (Default: 500 502
                        503 504 522 524 408 429)
  --url_retry_limit URL_RETRY_LIMIT
                        Maximum allowable number of retrial (Default: 4)
  --url_retry_wait_second URL_RETRY_WAIT_SECOND
                        Number of seconds to wait between two retrials
                        (Default: 60)
```

### Brief descriptions of behavior
- Starts N=```MAX_NUMBER_OF_CRAWLERS``` parallel-running crawlers, and N=```MAX_NUMBER_OF_DOC_PARSERS``` parallel-running document parsers
- Put URLs in ```SEED_TARGETS_LIST``` into crawlers' queue, followed by extracted links from crawled documents
- Crawlers process the URLs in FIFO manner
- When ```LOG_SHOW_LOG_LEVEL```=3, it shows a progress bar like this:

> 0d  170s URL:200|30000 Crawler:8/8 File: 100.0MB(33.3%)|   700(0.7%)
>> **0d  170s**: elapsed time
>>
>> **URL:200|30000**: URLs pending and to be crawled. 
>>
>> A URL will be pending for ```URL_RETRY_WAIT_SECOND``` seconds if it was refused (```URL_RETRY_HTTP_CODES```)
>>
>> **Crawler:8/8**: Running and total possible number of crawlers
>>
>> **File: 100.0MB(33.3%)|   700(0.7%)**: Storage status in terms of size and number of files, and their usage in %

- Keep crawling till all URLs are processed or storage limits (see Options) met

### Output
- a log file under ```LOG_FOLDER```
- crawled docs under ```STORAGE_FOLDER```
- a crawled doc is a json of the following format:
```
{
    "metadata": {
        "url": "https://en.wikipedia.org/wiki/Structured_prediction", 
        "url_depth": 1, 
        "anchor_text": "Structured prediction", 
        "creation_time": "2021-01-22 15:17:49", 
        "title": "Structured prediction - Wikipedia"
        }, 
    "document": '''<!DOCTYPE html>\n<html class=\"client-nojs\" dir=\"ltr\" lang=\"en\">\n<head>\n ...''',
}
```
