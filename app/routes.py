from flask import render_template, request, redirect, url_for, session
import pandas as pd
from app import app, client, gsheets_client

STYLE_GUIDE_SOURCE = 'https://docs.google.com/spreadsheets/d/1lwCCOReOyZS2ZmU0wT1fzgtOMGT9OdaQqGyDnE1ASy8/edit#gid=0'

# Converts a Google sheet to a dataframe for data manipulation
def sheets_to_df(wbk, sheet_name):
    data = wbk.worksheet(sheet_name).get_all_values()
    header = data[0]
    values = data[1:]

    all_data = []
    for col_id, col_name in enumerate(header):
        column_data = []
        for row in values:
            column_data.append(row[col_id])
        ds = pd.Series(data=column_data, name=col_name)
        all_data.append(ds)
    df = pd.concat(all_data, axis=1)
    return df

# Modifies all incoming requests to use https://
@app.before_request
def before_request():
    if request.url.startswith('http://'):
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)

# Added route to conveniently obtain oauth_token for a Foursquare account
@app.route('/get_access_token', methods=['GET', 'POST'])
def get_token():
    auth_uri = client.oauth.auth_url()
    return redirect(auth_uri, code=302)


@app.route('/redirect', methods=['GET', 'POST'])
def redir():
    code = request.args.get('code')
    access_token = client.oauth.get_token(code)
    return str(access_token)

@app.route('/<venue_id>/ls-proposeedit')
def ls_propose_edit(venue_id):

    wbk = gsheets_client.open_by_url(STYLE_GUIDE_SOURCE)

    other_params = {}
    params = {}

    # [FOR VISUALIZATION] Store the original params coming in from listing syndicators
    # other_params contains data that is cleaned.
    for key, value in request.args.items():
        params[key] = value
        other_params[key] = value

    # [FOR VISUALIZATION] Get the un-edited venue details with the Foursquare API
    fsq_result = client.venues(venue_id)
    original_details = {'name':fsq_result['venue'].get('name',''),
                        'address':fsq_result['venue']['location'].get('address',''),
                        'cc': fsq_result['venue']['location'].get('cc','')}

    # Pull the countrycode of the venue, since different regions may have conflicting
    # styling rules, and then pull the necessary rules from the GSheet.
    country_code = fsq_result['venue']['location'].get('cc','')

    # We then convert the rules for the necessary country into a dataframe
    rules_df = sheets_to_df(wbk, country_code)


    # Loop through all the rules to clean the data coming in from the listing syndicators
    for index,row in rules_df.iterrows():
        # This handles the REPLACE rule where we replace value1 with value2
        if "REPLACE" in row['rule']:
            fieldname = row['fieldname']
            to_replace = row['value1']
            replace_with = row['value2']
            other_params[fieldname] = other_params[fieldname].replace(to_replace, replace_with)

    # Cleaned data is then sent into the proposeedit endpoint and into our queues/database
    result = client.venues.proposeedit(venue_id,params=other_params)

    # [FOR VISUALIZATION]
    new_fsq_result = client.venues(venue_id)
    edited_details = {'name':new_fsq_result['venue'].get('name',''),
                        'address':new_fsq_result['venue']['location'].get('address',''),
                        'cc': new_fsq_result['venue']['location'].get('cc','')}
    return render_template('ls_propose_edit_viz.html',
                                original_details=original_details,
                                edited_details=edited_details,
                                other_params=other_params,
                                params=params,
                                result=result)
