
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

plt.style.use('ggplot')
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_rows', 25)
pd.set_option('display.max_colwidth', 100)
pd.set_option('display.precision', 3)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

import math
import time
from googleapiclient.discovery import build



# To avoid Youtube's limit on requesting large amounts of data,
# it's necessary to chunksize the timeframe in each call.
# This function allows searching query within a 24-hour window in each API call. 


def generate_date_ranges(start_date, end_date):
    date_ranges = []
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + datetime.timedelta(days=1)
        if next_date >= end_date:
            next_date = end_date
        date_ranges.append((current_date.strftime("%Y-%m-%dT%H:%M:%SZ"), next_date.strftime("%Y-%m-%dT%H:%M:%SZ")))
        current_date = next_date
    
    return date_ranges



# Communicate with Youtube's search.list() endpoint
def tube_keyword(api_key, queries, date_ranges, relevanceLanguage, order):
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos = []
    video_IDs= []
    channel_IDs=[]

    for i, (publishedAfter, publishedBefore) in enumerate(date_ranges):
        print(f"Processing videos for interval {i + 1} - published between {publishedAfter} and {publishedBefore}")

        # Initiate the initial API call to the search endpoint       
        # Here, 'queries' is a list of q separated by commas, thus allowing searching mulitple words or phrases at one go
        for query in queries:
            print(f"Searching videos mentioning this keyword or phrases: {query}")
            search_response = youtube.search().list(
                q=query,
                type='video',
                publishedAfter=publishedAfter,
                publishedBefore=publishedBefore,
                part='snippet',
                maxResults=50,
                relevanceLanguage=relevanceLanguage,
                order=order
            ).execute()

            total_results = search_response['pageInfo']['totalResults']
            print(f"Total Results: {total_results}")

            # Unpack the initial response
            for item in search_response['items']:
                if item['id']['videoId'] not in video_IDs:
                    video_data = {
                        'video_id': item['id']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'publishedAt': item['snippet']['publishedAt'],
                        'channelId': item['snippet']['channelId'],
                        'channelTitle': item['snippet']['channelTitle'],
                        'thumbnails': item['snippet']['thumbnails']['default']['url']
                                 }
                              
                    video_IDs.append(item['id']['videoId'])
                    videos.append(video_data)
                    
                    # Save unique channel id into a list for retrieving channel info
                    if item['snippet']['channelId'] not in channel_IDs:
                        channel_IDs.append(item['snippet']['channelId'])

            next_page_token = search_response.get('nextPageToken')
            
            while next_page_token is not None:
                search_response = youtube.search().list(
                    q=query,
                   type='video',
                    publishedAfter=publishedAfter,
                    publishedBefore=publishedBefore,
                    part='snippet',
                    maxResults=50,
                    relevanceLanguage=relevanceLanguage,
                    order=order,
                    pageToken=next_page_token
                ).execute()
                
                # Unpack responses from subsequent paginations
                for item in search_response['items']:
                    if item['id']['videoId'] not in video_IDs:
                        video_data = {
                            'video_id': item['id']['videoId'],
                            'title': item['snippet']['title'],
                            'description': item['snippet']['description'],
                            'publishedAt': item['snippet']['publishedAt'],
                            'channelId': item['snippet']['channelId'],
                            'channelTitle': item['snippet']['channelTitle'],
                            'thumbnails': item['snippet']['thumbnails']['default']['url']
                                     }

                        video_IDs.append(item['id']['videoId'])
                        videos.append(video_data)

                        if item['snippet']['channelId'] not in channel_IDs:
                            channel_IDs.append(item['snippet']['channelId'])
                
                # Get the next page token, if there is any
                next_page_token = search_response.get('nextPageToken')

    return videos, video_IDs, channel_IDs


# Communicate with Youtube's video.list() endpoint for individual videos' meatadata
def tube_meta(video_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_responses = []

    chunk_size = 50
    num_chunks = math.ceil(len(video_id) / chunk_size)

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size
        current_chunk = video_id[start_index:end_index]

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=current_chunk,
            maxResults=50,
            pageToken=None
        )

        response = request.execute()
        all_responses.append(response)

        print(f"Video metadata list_{i + 1} fetched")
        print('---------')
        
    print(f"Finished fetching ALL {num_chunks} chunks of video metadata")
    
    video_metadata=[]
    for each_response in all_responses:
        for item in each_response['items']:
            v_metadata = {
                'video_id': item['id'],
                'video_defaultLanguage': item['snippet'].get('defaultLanguage', np.nan),
                'video_defaultAudioLanguage': item['snippet'].get('defaultAudioLanguage', np.nan),
                'video_categoryId': item['snippet'].get('categoryId', np.nan),
                'video_duration': item['contentDetails'].get('duration', np.nan),
                'video_caption': item['contentDetails'].get('caption', np.nan),
                'video_licensedContent': item['contentDetails'].get('licensedContent', np.nan),
                'video_viewCount': item['statistics'].get('viewCount', np.nan),
                'video_likeCount': item['statistics'].get('likeCount', np.nan),
                'video_commentCount': item['statistics'].get('commentCount', np.nan)
                        }
            video_metadata.append(v_metadata)

    return video_metadata



# # Communicate with Youtube's channel.list() endpoint for channel metadata
def tube_channel(channel_id, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    all_responses = []  
    chunk_size = 50
    num_chunks = math.ceil(len(channel_id) / chunk_size)

    for i in range(num_chunks):
        start_index = i * chunk_size
        end_index = (i + 1) * chunk_size
        current_chunk = channel_id[start_index:end_index]

        request = youtube.channels().list(
            part='snippet, statistics, contentDetails, topicDetails, status',
            id=current_chunk,
            maxResults=50,
            pageToken=None
        )

        response = request.execute()
        all_responses.append(response)
        print(f"Channel metadata list_{i + 1} fetched")
        print(f"-------------")

    print(f"Finished fetching ALL {num_chunks} chunks of channel metadata")
    
    channel_metadata=[]
    for each_response in all_responses:
        for item in each_response['items']:
            c_metadata={
                'channel_id':item['id'],
                'channel_title': item['snippet'].get('title', np.nan),
                'channel_description': item['snippet'].get('description', np.nan),
                'channel_publishedAt': item['snippet'].get('publishedAt', np.nan),
                'channel_viewCount': item['statistics'].get('viewCount', np.nan),
                'channel_subscriberCount': item['statistics'].get('subscriberCount', np.nan),
                'channel_videoCount': item['statistics'].get('videoCount', np.nan),
                'channel_country': item['snippet'].get('country', np.nan)    
                
            }
            channel_metadata.append(c_metadata)

    return channel_metadata




# This function organizes all returned data and metadata into one single dataframe
def searchtube(api_key, queries, date_ranges, relevanceLanguage, order):
    # Sending the searching video request
    videos, video_IDs, channel_IDs = tube_keyword(api_key, queries, date_ranges, relevanceLanguage, order)

    # Sending the video metadata request
    video_metadata = tube_meta(video_IDs, api_key)

    # Sending the channel metadata request
    channel_metadata = tube_channel(channel_IDs, api_key)

    # Video -> dataframea
    df_tube = pd.DataFrame(videos)

    # Video metadata -> dataframe
    df_meta = pd.json_normalize(video_metadata)

    # Channel metadata -> dataframe
    df_channel = pd.json_normalize(channel_metadata)

    # Merge all three dataframes, drop duplicated and clean up the columns a bit
    df = pd.merge(df_tube, df_meta, how='left', on='video_id')
    df = pd.merge(df, df_channel, how='left', left_on='channelId', right_on='channel_id')
    df = df.drop(columns=['channelId','channelTitle'])
    df = df.drop_duplicates(subset='video_id', keep='first')

    return df


if __name__ == "__main__":
    api_key = 'api key'
    queries = 'search query'
    start_date = 'datetime.datetime(#format example: 2024,2,1)'
    end_date = 'datetime.datetime(#format example: 2024,2,29)'
    date_ranges = '[(start_date.strftime("%Y-%m-%dT%H:%M:%SZ"), end_date.strftime("%Y-%m-%dT%H:%M:%SZ")) for start_date, end_date in generate_date_ranges(start_date, end_date, interval_days)]'
    relevanceLanguage= 'en'
    order = '# None or default is "relevance", other options include "date", "rating", "title", "videoCount", and "viewCount"'
    df =' searchtube(api_key, queries, date_ranges, relevanceLanguage, order)'

