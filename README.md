# Wx Twitter Bot

A bot that tweets about the weather.

## Capabilities

- Solar Times (sunrise, noon, sunset)
- Lunar Times (moonrise, illumination, moonset)

## Quick Start

In order to use this application with Twitter, developer credentials are required. Get them [here](https://developer.twitter.com/).

## Environment Variables

| Name | Description |
| ---- | ----------- |
| `DATA_DIR` | Specifies the directory where the data files will be stored (optional, default = `./data/`) |
| `LOG_DIR` | Specifies the directory where the log file will exist (optional, default = `./log/`) |
| `LOG_LEVEL` | Specifies the level of logging to use when executing the application (e.g. "DEBUG") |
| `LOCATION` | A label for the location associated the this instance of the application |
| `REGION` | A label for the location's region associated with this instance of the application |
| `TIMEZONE` | The timezone name for the location associated with this instance of the application from the "tz database" |
| `LATITUDE` | The latitude for the location associated with this application, decimal format |
| `LONGITUDE` | The longitude for the location associated with this application, decimal format |
| `TWITTER_CONSUMER_KEY` | The consumer key for the Twitter API |
| `TWITTER_CONSUMER_SECRET` | The consumer secret for the Twitter API |
| `TWITTER_ACCESS_TOKEN` | The access token for the Twitter API |
| `TWITTER_ACCESS_TOKEN_SECRET` | The access token secret for the Twitter API |

## License

[MIT License](https://github.com/jnsnkrllive/wx-twitter-bot/blob/master/LICENSE)
