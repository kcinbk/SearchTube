# SearchTube

SearchTube is a Python-based wrapper and allows querying YouTube videos or channels by keywords. The returning data is structured in pandas DataFrames.

One of the major improvements of this version is its efficiency, as it combines various YouTube endpoints into one and returns both video and channel metadata. The wrapper also circumvents the several limits on result quantity regulated by YouTube by automatically dividing the search timeframe. This is particularly useful in scenarios where a large amount of data is requested or for covering a longer period of time for academic or journalistic research.