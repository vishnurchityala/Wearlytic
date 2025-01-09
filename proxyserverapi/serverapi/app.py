from klein import Klein
import subprocess
import json
from twisted.internet.defer import inlineCallbacks
from twisted.internet import defer

app = Klein()

# Define the route for triggering the Scrapy spider
@app.route('/fetch', methods=['GET'])
@inlineCallbacks
def fetch_page(request):
    url = request.args.get('url', [None])[0]

    if not url:
        return json.dumps({'error': 'No URL provided'}), 400

    try:
        # Run Scrapy spider using subprocess
        command = ['scrapy', 'crawl', 'page_spider', '-a', f'url={url}']

        # Run the command and capture the output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Capture the standard output and error streams
        stdout, stderr = yield deferToThread(process.communicate)

        if process.returncode == 0:
            return json.dumps({
                'message': 'Scraping completed successfully!',
                'data': stdout,  # Return the output of the Scrapy spider
                'logs': stdout,  # Scrapy logs
                'error_logs': stderr if stderr else 'No errors'
            }), 200
        else:
            # If Scrapy failed, return stderr error details
            return json.dumps({
                'error': 'Scrapy process failed',
                'stderr': stderr
            }), 500

    except Exception as e:
        return json.dumps({'error': str(e)}), 500


# Start the Klein app to listen on a specific port
if __name__ == '__main__':
    app.run("localhost", 3000)
