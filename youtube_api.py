# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

f = open('./Songaday/client_secret_209554330154-ma12788ji9590jocsudhitotedt0ogca.apps.googleusercontent.com.json')

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    #os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
def getYTstats(ids):
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "./Songaday/client_secret_209554330154-ma12788ji9590jocsudhitotedt0ogca.apps.googleusercontent.com.json"
    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    #
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=ids
    )
    response = request.execute()
    #
    return response['items']


if __name__ == "__main__":
    results = getYTstats(sad_ids)

ids = list()
views = list()
likes = list()
comments = list()
for i in list(range(len(results))):
    ids.append( results[i]['id'] )
    views.append( results[i]['statistics']['viewCount'] )
    likes.append( results[i]['statistics']['likeCount'] )
    comments.append( results[i]['statistics']['commentCount'] )

