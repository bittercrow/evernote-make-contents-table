#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

# 1 Generate a Temporary Token
# 2 Request User Authorization
# 3 Retrieve Access Token
# 4 Next Steps for Accessing the API

import json
from urlparse import urlparse, parse_qs
import os
from wsgiref.simple_server import make_server
from evernote.api.client import EvernoteClient
import evernote.edam.error.ttypes as Errors 
from evernote.edam.error.ttypes import EDAMErrorCode
import MakeContents

try:
    here = os.path.dirname(__file__)
    with open(here + '/app_data.json') as f:
        app_data = json.load(f)
    with open(here + '/template.html') as f:
        html = f.read()
    with open(here + '/styles.css') as f:
        styles_file = f.read()

except IOError as e:
    print e
    print 'File missing. Run \'MakeJson.py\''


messages = {
    'connect': 'If you have an Evernote account, click \"Connect\" below',
    'reconnect': '{}<br>Please reconnect', 
    'active': 'Active:',
    'complete': 'Complete',
}

html_body = {
    'message': '',
    'control_div': '',
}

HOST_URL = app_data['HOST_URL']
host = urlparse(HOST_URL).netloc.split(':')[0]
port = int(urlparse(HOST_URL).netloc.split(':')[1])
callback_url = HOST_URL + '/callback'
makecontents_url = HOST_URL + '/makecontents'

# Set my API key
temp_client = EvernoteClient(
    consumer_key=app_data['consumer_key'],
    consumer_secret=app_data['consumer_secret'],
    sandbox=app_data['sandbox']
)
temp_token = temp_client.get_request_token(callback_url)
if 'oauth_callback_confirmed' in temp_token:
    if not temp_token['oauth_callback_confirmed']:
        raise Exception('Error: oauth_callback_confirmed = False')
else:
    raise Exception('Error: No oauth_callback_confirmed')
auth_url = temp_client.get_authorize_url(temp_token)
oauth_info = {
    'oauth_token': temp_token['oauth_token'],
    'oauth_token_secret': temp_token['oauth_token_secret'],
    'oauth_verifier': '',
}


def connect_div(url):
    '''Return auth div'''
    return '<a href={}>Connect</a>'.format(url)


def makecontents_div(url):
    '''Return makecontents div''' 
    return '<a href={}>\
    <div>Make tables of contents</div>\
    <img src="ball.png" alt="makecontents" width="100" height="100">\
    </a>'.format(url)


def access_token(oauth_info):
    return temp_client.get_access_token(
        oauth_info['oauth_token'],
        oauth_info['oauth_token_secret'],
        oauth_info['oauth_verifier']
    )


def store_token(token):
    app_data['token'] = token
    with open(here + '/app_data.json', 'w') as f:   
        json.dump(app_data, f, indent=4) 


def test_task(environ, start_response):
    # oauth_verifier=147C06F04031FE509622A7A1354FFE5C
    # https://sandbox.evernote.com/OAuth.action?oauth_token=ts-2012.16764416D57.68747470733A2F2F73616E64626F782E657665726E6F74652E636F6D2F4F417574682E616374696F6E.6ED4C156CA21C55EC6A53B928C56EB9C&oauth_verifier=2FB6AEB9819680C2D36D1E6A0037CB39&sandbox_lnb=false
    start_response("200 OK", [("Content-type", "text/html;charset=utf-8")])
    try:
        client = EvernoteClient(
            token=app_data['token'],
            sandbox=app_data['sandbox'],
            china=app_data['china'])
        note_store = client.get_note_store()
        notebooks = note_store.listNotebooks()
        for n in notebooks:
            print n.name
        html_body['message'] = 'Test has been done.'
        html_body['control_div'] = makecontents_div(makecontents_url)
        return [html.format(**html_body)]
    except Errors.EDAMUserException as e:
        err = EDAMErrorCode._VALUES_TO_NAMES[e.errorCode] 
        param = e.parameter
        msg = 'Authentication failed. {} - {}'.format(err, param)
        html_body['message'] = messages['reconnect'].format(msg)
        html_body['control_div'] = connect_div(auth_url)
        return [html.format(**html_body)]


def home(environ, start_response):
    start_response("200 OK", [("Content-type", "text/html;charset=utf-8")])
    if app_data['token']:
        html_body['message'] = messages['active']
        html_body['control_div'] = makecontents_div(makecontents_url)
        return [html.format(**html_body)]
    else:
        html_body['message'] = messages['connect']
        html_body['control_div'] = connect_div(auth_url)
        return [html.format(**html_body)]


def callback(environ, start_response):
    ''' '''
    start_response("200 OK", [("Content-type", "text/html;charset=utf-8")])
    query_string = environ['QUERY_STRING']
    params = parse_qs(query_string)
    if 'oauth_verifier' in params:
        oauth_info['oauth_verifier'] = params.get('oauth_verifier')[0]
        token = access_token(oauth_info)
        store_token(token)
        html_body['message'] = messages['active']
        html_body['control_div'] = makecontents_div(makecontents_url)
        return [html.format(**html_body)]
    else:
        comment = 'Not granted the application to your Evernote account: {}'
        reason = params.get('reason')[0]
        msg = comment.format(reason)
        html_body['message'] = messages['reconnect'].format(msg)
        html_body['control_div'] = connect_div(auth_url)
        return [html.format(**html_body)]


def tryagain(environ, start_response):
    # html_body['message'] = messages['reconnect'].fomrat(reason)
    # html_body['control_div'] = makecontents_div(makecontents_url)
    # return [html.format(**html_body)]
    pass


def makecontents(environ, start_response):
    start_response("200 OK", [("Content-type", "text/html;charset=utf-8")])
    client = EvernoteClient(
        token=app_data['token'],
        sandbox=app_data['sandbox'],
        china=app_data['china'])
    res, msg = MakeContents.main(client)
    if res:
        html_body['message'] = msg
        html_body['control_div'] = makecontents_div(makecontents_url)
        return [html.format(**html_body)]
    else:
        html_body['message'] = messages['reconnect'].format(msg)
        html_body['control_div'] = connect_div(auth_url)
        return [html.format(**html_body)]


def styles(environ, start_response):
    '''Response style.css'''
    start_response("200 OK", [("Content-type", "text/css;charset=utf-8")])
    return [styles_file]


def ball_img(environ, start_response):
    '''Response the ball image'''
    start_response("200 OK", [("Content-type", "image/png")])
    return [open('./ball.png', 'rb').read()] 

    
routes = [
    ('/', home),
    ('/callback', callback),
    ('/tryagain', tryagain),
    ('/makecontents', makecontents),
    ('/test_task', test_task),
    ('/styles.css', styles),
    ('/ball.png', ball_img),
]


def routing(environ, start_response):
    ''''''    
    request_path = environ['PATH_INFO']
    for path, func in routes:
        if path == request_path:            
            return func(environ, start_response)
    start_response("404 Not Found", [("Content-type", "text/plain;charset=utf-8")])    
    return ['Not Found: {}'.format(request_path).encode('utf-8')]


def app(environ, start_response):
    ''' WSGI Application '''
    method = environ['REQUEST_METHOD']
    if method == 'GET':
        return routing(environ, start_response)
    else:
        start_response('501 Not Implemented', [('Content-type', 'text/plain;charset=utf-8')])
        return ['Not Implemented'.encode('utf-8')]


def main():
    '''Simple Server'''
    httpd = make_server(host, port, app)
    print u"Server starts"
    print app_data['HOST_URL']
    print u"Press Ctrl + 'c' to stop"
    httpd.serve_forever()


if __name__ == '__main__':
    main()