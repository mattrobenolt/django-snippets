# JsonResponse

## Usage:
```python
from http.json import JsonResponse

def json_response(request):
    return JsonResponse({"key": "value"})
```
# TwimlResponse

## Usage:
```python
from http.twilio import TwimlResponse
from twilio import twiml

def hello_world(response):
    """Shortcut to twiml.Say("Hello world!")"""
    return TwimlResponse("Hello world!")

def hello_world2(response):
    """Shortcut to responding with any Twilio Response object."""
    r = twiml.Response()
    r.say("Hello world!")
    return TwimlResponse(r)

def hello_world3(response):
    """Shortcut to responding with an SMS."""
    return TwimlResponse("Hello world!", verb="sms")
```