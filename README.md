# fmonitor
Simple monitoring application written in Python.

## Running
Best way to run the application is inside a docker container.
```shell
# Build image
docker image build -t fmonitor .

# Run
docker container run --rm --name fmonitor fmonitor
```
If you prefer to run it in a virtual environemnt
```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## Configuratiom
Edit the file `settings.json` to configure the application:
- `urls`: List of websites and their conditions. 
- `interval`: set frequency of requests in seconds. (optional)
- `workers`: set number of worker threads. (optional)

for example:
```json
{
    "interval": 5,
    "workers": 4,
    "urls": [
        {
            "url": "http://www.google.com",
            "condition": "Google"
        },
        {
            "url": "http://httpstat.us/400"
        }
    ]
}
```

## How it works
When you start the application it does couple of things:
- Loads settings file
- Validate settings file
- Creates an empty queue
- Start couple of worker threads (default 5)
- Start main loop

The loop each time loads the website urls and conditions in the queue and then sleeps for an interval (default 5 seconds). 

When the queue has items in them they get automatically picked by the worker threads that each call `process_url` to process the url, you can tune the number of worker threads depending on the size of the url list.

`process_url` function on the other hand, performs HTTP GET request to the url specified and then logs the result to `stdout`

## Output
The website status log format is as follows:

```
'URL: {url}, Time (s): {time}, Result: {result}, Reason: {reason}'
```

Where:
- url: Url of the website
- time: elaspsed time of the request
- result: `Success` or `Failure`
- reason: if result is `Failure` reason contains either:
    - `ConditionNotMet`: Response does not container the text provided
    - `RequestException`: Request error (including server/http error responses)


## Test
To run the test suite run pytest:
```shell
python -m pytest --cov=fmonitor --cov-report term-missing .
```
