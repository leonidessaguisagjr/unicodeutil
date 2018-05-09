#!/usr/bin/env python3

import os.path
import re

from flask import Flask, abort, jsonify, make_response, redirect, render_template, request, url_for

from unicodeutil import UnicodeData, casefold, UNIDATA_VERSION
from unicodeutil.unicodeutil import _unichr

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
appname = "unicodeutil"
api_version = "v1.0"
api_base_url = "/{0}/api/{1}/".format(appname, api_version)
ui_base_url = "/{0}/".format(appname)
ucd_base_url = "{0}ucd/".format(ui_base_url)
ucd = UnicodeData()


@app.errorhandler(404)
def handle_404(error):
    return make_response(jsonify({"error": "URL not found.  Please check your spelling and try again."}), 404)


@app.route(api_base_url + "ucd/<lookup>", methods=['GET'])
def ucd_lookup(lookup):
    try:
        lookup_value = int(lookup, 16)
    except ValueError:
        abort(404)
        return
    char_info = ucd[lookup_value]
    if not char_info:
        abort(404)
    response = char_info._asdict()
    return jsonify(response)


@app.route(api_base_url + "casefold", methods=['POST'])
def do_casefold():
    fullcasefold = request.json['fullcasefold'] if 'fullcasefold' in request.get_json() else True
    useturkicmapping = request.json['useturkicmapping'] if 'useturkicmapping' in request.get_json() else False
    return jsonify(casefold(request.json['input_string'], fullcasefold=fullcasefold, useturkicmapping=useturkicmapping))


@app.route("/")
def home():
    return redirect(ucd_base_url)


@app.route(ucd_base_url, methods=['GET', 'POST'])
def ucd_html():
    if request.method == "POST":
        search_type = "value" if "lookup_by_value" in request.form else "name"
        search_text_input = request.form.get('search_text_input')
        if not search_text_input:
            return render_template("ucdlookup_error_template.html", search_text_input=search_text_input, search_type=search_type)
        try:
            if "lookup_by_value" in request.form:
                lookup = re.sub(r"^[Uu]\+", "", search_text_input)  # Strip leading "U+" or "u+" if it is present.
                ucd[int(lookup, 16)]  # Try doing a lookup so we can trap the KeyError and render the error page.
            else:
                lookup = ucd.lookup_by_name(search_text_input).code[2:]  # Strip the leading "U+"
        except (KeyError, ValueError):
            return render_template("ucdlookup_error_template.html", search_text_input=search_text_input, search_type=search_type)
        return redirect("/unicodeutil/ucd/" + lookup)
    else:
        return render_template("ucdlookup_template.html")


@app.route(ucd_base_url + "<lookup>", methods=['GET'])
def charinfo_html(lookup):
    try:
        lookup_value = int(lookup, 16)
    except ValueError:
        abort(404)
        return
    char_info = ucd[lookup_value]
    if not char_info:
        abort(404)
    return render_template("charinfo_template.html", char=_unichr(lookup_value), char_info=char_info._asdict(),
                           ucd_ver=UNIDATA_VERSION)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
