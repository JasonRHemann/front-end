import re
import argparse
import flask
from flask import request
from werkzeug.serving import run_simple
# from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Importing from Plotly Dash
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc

# Imports from this application
from app import app, server
from layout.desktop_layout import build_desktop_layout
from layout.mobile_layout import build_mobile_layout
from pages import desktop, navbar, footer
from pages import about_body, resources_body
from pages import mobile, mobile_navbar, mobile_footer
from pages import mobile_about_body, mobile_resources_body


# Set default layout so Flask can start
app.layout = build_desktop_layout


@server.before_request
def before_request_func():
    """Checks if user agent is from mobile to determine which layout to serve before
    user makes any requests.
    """
    agent = request.headers.get("User_Agent")
    mobile_string = "(?i)android|fennec|iemobile|iphone|opera (?:mini|mobi)|mobile"
    re_mobile = re.compile(mobile_string)
    is_mobile = len(re_mobile.findall(agent)) > 0

    # print(f'[DEBUG]: Requests from Mobile? {is_mobile}')
    if is_mobile:
        app.layout = build_mobile_layout
        flask.session['mobile'] = True#f"{app_state.is_mobile}"
        flask.session['zoom'] = 2
    else:  # Desktop request
        app.layout = build_desktop_layout
        flask.session['mobile'] = False#f"{app_state.is_mobile}"
        flask.session['zoom'] = 3
    
    # print(f"[DEBUG]: Session: 'mobile': {flask.session['mobile']}, 'zoom': {flask.session['zoom']}")
        

@app.callback([Output("navbar-content", "children"),
               Output("page-content", "children"),
               Output("footer-content", "children")],
              [Input("url", "pathname")])
def display_page(pathname):
    is_mobile = flask.session['mobile']
    # print(f"[DEBUG]: Session: 'mobile': {flask.session['mobile']}")

    if pathname == "/":
        if is_mobile:
            return mobile_navbar, mobile.mobile_body, mobile_footer
        else:
            return navbar, desktop.desktop_body, footer
    elif pathname == "/about":
        if is_mobile:
            return mobile_navbar, mobile_about_body, mobile_footer
        else:
            return navbar, about_body, footer
    elif pathname == "/resources":
        if is_mobile:
            return mobile_navbar, mobile_resources_body, mobile_footer
        else:
            return navbar, resources_body, footer
    else:
        error_page = [dcc.Markdown("404: PAGE NOT FOUND")]
        if is_mobile:
            return mobile_navbar, error_page, mobile_footer
        else:
            return navbar, error_page, footer

# Combining Flask and Dash apps
application = DispatcherMiddleware(server, {
    "": app.server,
})

if __name__ == "__main__":
    run_simple('127.0.0.1', 8050, application)
    # app.run_server(debug=True)