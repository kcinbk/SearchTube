# SearchTube



## About this project
SearchTube is a YouTube API wrapper that integrates search, video and channel endpoints, allowing you to query by keywords or hashtags and return all major metadata.

One of the major improvements in this version its efficiency, beacuse it:
1. Allows your to query a list of multiple keywords simultaneously; 
2. Chunsize the returned data to bypass rate limits and other poorly documented restrictions. This is particularly useful when requesting large amounts of data or covering extended periods for academic or journalistic research.


## Getting Started
### Requirement 
<a href="https://developers.google.com/youtube/v3/live/registering_an_application">YouTube API v3 authorization credential</a>. 

### Installing
 ````bash
pip install git+https://github.com/kcinbk/SearchTube.git
````

### Importing
````python
import searchYouTube 
````

### Quering YouTube content by multiple keywords
````python
data = searchYouTube.search.fetch_tiktok(client_key, client_secret, search_query, start_date, end_date)
````

## Contact the author
<a href="https://kcinbk.github.io">Keenan Chen</a>.



