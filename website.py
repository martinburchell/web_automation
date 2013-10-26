import cookielib
import tempfile
import urllib2

from lxml.html.soupparser import fromstring

from retry import retry

class Website(object):
    debug = False

    def __init__(self, domain, login=None, password=None, logger=None):
        cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
        self.insecure_domain = 'http://' + domain
        self.secure_domain = 'https://' + domain
        self.login = login
        self.password = password
        self.logger = logger

    def download_to_file(self, url):
        content = self.read_content(url)
        
        file = tempfile.NamedTemporaryFile(delete=False)
        file.write(content)
        file.close

        return file.name

    def send_request_and_return_dom(self, url, post_data=None):
        content = self.read_content(url, post_data)

        return fromstring(content)

    def read_content(self, url, post_data=None):
        response = self.send_request_with_retry(url, post_data)
        content = response.read()
        response.close()

        return content

    @retry(urllib2.URLError, tries=4, delay=3, backoff=2)
    def send_request_with_retry(self, url, post_data):
        return self.opener.open(url, post_data)

    def is_up(self):
        try:
            self.opener.open(self.insecure_domain)
        except urllib2.URLError:
            return False

        return True

