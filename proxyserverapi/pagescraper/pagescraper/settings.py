# Scrapy settings for pagescraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "pagescraper"

SPIDER_MODULES = ["pagescraper.spiders"]
NEWSPIDER_MODULE = "pagescraper.spiders"

#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
# See also autothrottle settings and docs
# Disable obeying robots.txt as ACM might block scraping
ROBOTSTXT_OBEY = False

# Request fingerprinter for Scrapy 2.7 and newer
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Use Asyncio reactor to avoid compatibility issues
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Set feed export encoding to UTF-8
FEED_EXPORT_ENCODING = "utf-8"

# Enable handling of cookies
COOKIES_ENABLED = True

# Enable redirection handling
REDIRECT_ENABLED = True

# Set a limit on how many times a request can be redirected
REDIRECT_MAX_TIMES = 5  # Prevent getting stuck in redirection loops

# Define the user agent to mimic a browser and prevent blocking
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Add a download delay to avoid being flagged for scraping too fast
DOWNLOAD_DELAY = 1

# Enable retries in case of failed requests or server-side issues
RETRY_ENABLED = True
RETRY_TIMES = 5  # Retry up to 5 times for failed requests

# Use the default duplicate filter
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Logging settings for debugging
LOG_LEVEL = 'DEBUG'

# (Optional) Adjust memory usage monitoring
MEMUSAGE_ENABLED = True

# Enable the telnet console for debugging while the spider is running
TELNETCONSOLE_ENABLED = True

# Enable extensions
EXTENSIONS = {
    'scrapy.extensions.corestats.CoreStats': 500,
    'scrapy.extensions.logstats.LogStats': 500,
    'scrapy.extensions.memusage.MemoryUsage': 500,
    'scrapy.extensions.feedexport.FeedExporter': 500,
    'scrapy.extensions.telnet.TelnetConsole': None,  # Adjust if needed
}

# Enable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
}

# Enable spider middlewares
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 100,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 200,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 300,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 400,
}

# Enable item pipelines (if needed)
ITEM_PIPELINES = {
    # Add your pipelines here if you're processing scraped data
}

# Configure Scrapy-Splash
SPLASH_URL = 'http://localhost:8050'

# Use Splash for all requests
DOWNLOADER_MIDDLEWARES.update({
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
})

# Add Scrapy-Splash settings
SPLASH_COOKIES_ENABLED = True
SPLASH_HTTP_CACHE_ENABLED = True
SPLASH_HTTP_CACHE_DIR = 'splash_cache'

# Scheduler settings
SCHEDULER = 'scrapy.core.scheduler.Scheduler'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
