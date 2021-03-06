import re

from . import constants
from .URL import URL
from .util import get_domain_from_url

from urllib.parse import urlparse, urldefrag
from urllib.robotparser import RobotFileParser

class URLMgr:
    def __init__(self, config, logger):
        self._config = config
        self._logger = logger
        self._urls = list()
        self._idxs = list()
        self._robots = dict()
        self._idxs_set = set()
        self._url_strs_set = set()
        self._active_idxs_set = set()
        
    def check_is_url_str_valid(self, url_str):
        parsed = urlparse(url_str)
        
        if len(url_str) > self._config.URL_MAX_LENGTH:
            self._logger.add(constants.WARNING, url_str, ':URL Length over limit.')
            return False
        elif parsed.path.count('\\') > self._config.URL_MAX_NUM_SLASHES:
            self._logger.add(constants.WARNING, url_str, ':Number of slashes over limit.')
            return False
        elif not re.match(self._config.URL_PATTERN, url_str):
            self._logger.add(constants.WARNING, url_str, ':Invalid URL.')
            return False
        else:
            return True
            
    def check_is_new_url_str(self, url_str):
        if url_str in self._url_strs_set:
            self._logger.add(constants.WARNING, url_str, ':URL added previously')
            return False
        else:
            return True
            
    def check_robot_can_fetch(self, url_str):
        domain = get_domain_from_url(url_str)
        if domain not in self._robots:
            self._logger.add(constants.WARNING, url_str, ':Getting robots.txt')
            self._robots[domain] = RobotFileParser('{domain}/robots.txt'.format(domain=domain))
            try:
                self._robots[domain].read()
            except:
                pass
        
        if self._robots[domain].can_fetch('*', url_str):
            return True
        else:
            self._logger.add(constants.WARNING, url_str, ':URL not allowed by Robots.txt')
            return False
    
    def check_is_valid_domain(self, url_str):
        pattern = '(%s)'%('|'.join(self._config.URL_ALLOWED_DOMAIN))
        if re.search(pattern, urlparse(url_str).netloc):
            return True
        else:
            self._logger.add(constants.WARNING, url_str, ':Not allowed domain')
            return False
    
    def check_is_URL_not_disallowed(self, url_str):
        pattern = '(%s)'%('|'.join(self._config.URL_DISALLOWED_URL))
        if re.search(pattern, url_str):
            self._logger.add(constants.WARNING, url_str, ':Not allowed URL')
            return False
        else:
            return True
            
    def check_is_new_url(self, url):
        if url.idx in self._idxs_set:
            self._logger.add(constants.WARNING, url.url_str, ':URL added previously')
            return False
        else:
            return True
        
    def check_is_URL_valid(self, url):
        if url.depth > self._config.URL_MAX_DEPTH:
            self._logger.add(constants.WARNING, url.url_str, ':URL depth over limit.')
            return False
        elif url.num_retry > self._config.URL_RETRY_LIMIT:
            self._logger.add(constants.WARNING, url.url_str, ':URL retry over limit.')
            return False
        else:
            return True
        
    def check_url_is_ready(self, url):
        return url.last_failed_ts is None\
                or url.last_failed_ts + self._config.URL_RETRY_WAIT_SECOND < dt.timestamp(dt.now())
        
    def set(self, url_str_or_URL, anchor_text=None, parent_URL=None):
        if isinstance(url_str_or_URL, str):
            url_str = urldefrag(url_str_or_URL).url
            if url_str != url_str_or_URL:
                self._logger.add(constants.WARNING, url_str, ':Defragged from', url_str_or_URL)
            
            idx = len(self._urls)
            url = URL(url_str, idx, anchor_text, parent_URL)
            
            if self.check_is_new_url_str(url_str)\
                and self.check_is_valid_domain(url_str)\
                and self.check_is_URL_not_disallowed(url_str)\
                and self.check_is_url_str_valid(url_str)\
                and self.check_robot_can_fetch(url_str)\
                and self.check_is_URL_valid(url):
                self._idxs.append(idx)
                self._idxs_set.add(idx)
                self._active_idxs_set.add(idx)
                self._urls.append(url)
                self._url_strs_set.add(url_str)
                self._logger.add(constants.INFO, url_str, ':URL added to queue')
        
        elif isinstance(url_str_or_URL, URL):
            url = url_str_or_URL
            idx = url.idx
            url.failed_once()
            if self.check_is_new_url(url)\
                and self.check_is_URL_valid(url):
                self._idxs.append(idx)
                self._idxs_set.add(idx)
                self._idxs = sorted(self._idxs)
                self._logger.add(constants.INFO, url.url_str, ':URL re-added to queue')
        
        else:
            raise NotImplemented
        
    def get(self, fifo=True):
        for idx in (self._idxs if fifo else reversed(self._idxs)):
            url = self._urls[idx]
            if self.check_url_is_ready(url):
                self._idxs.remove(idx)
                self._idxs_set.remove(idx)
                yield url
                
    def deactive_url(self, url):
        self._active_idxs_set.remove(url.idx)
                
    @property
    def num_URLs(self):
        return len(self._idxs)

    @property
    def num_active_URLs(self):
        return len(self._active_idxs_set)