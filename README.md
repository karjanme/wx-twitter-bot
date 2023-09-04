[release-image]: https://img.shields.io/github/v/release/karjanme/wx-twitter-bot
[release-url]: https://ghcr.io/karjanme/wx-twitter-bot

[![Release][release-image]][release-url]

# Wx Twitter Bot

A bot that tweets about the weather.

## Capabilities

- Solar Times (sunrise, noon, sunset)
- Lunar Times (moonrise, illumination, moonset)
- Air Quality

## Quick Start

In order to use this application with Twitter, developer credentials are required. Get them [here](https://developer.twitter.com/).

### Command Line

To run this application via the command line, execute the following from the project root directory:

```
python src/main.py [options]
```

Options:
| Name | Description |
| ---- | ----------- |
| `--app-root` | Path to the application root directory which contains the `.env` file. |

### Docker

This application can be run in a docker container using a published image.

For example:
```
docker pull ghcr.io/karjanme/wx-twitter-bot:latest
```

Configure the `TZ` environment variable when setting up the container.

Required volume mapping:
| Volume | Description |
| ------ | ----------- |
| `/app` | Must point to a directory on your host which contains the `.env` file. <br /> The appliation will create subdirectories to facilitate runtime needs. |

## Environment Variables

The following variables can be set using a `.env` file placed in the application root directory.

| Name | Description |
| ---- | ----------- |
| `LOG_LEVEL` | (optional) Specifies the [level](https://docs.python.org/3/library/logging.html#levels) of logging to use when executing the application (Default = "INFO") |
| `LOCATION` | A label for the location associated the this instance of the application |
| `REGION` | A label for the location's region associated with this instance of the application |
| `TIMEZONE` | The timezone name for the location associated with this instance of the application from the "tz database" |
| `LATITUDE` | The latitude for the location associated with this application, decimal format |
| `LONGITUDE` | The longitude for the location associated with this application, decimal format |
| `AIR_NOW_API_KEY` | TODO |
| `TWITTER_CONSUMER_KEY` | The consumer key for the Twitter API |
| `TWITTER_CONSUMER_SECRET` | The consumer secret for the Twitter API |
| `TWITTER_ACCESS_TOKEN` | The access token for the Twitter API |
| `TWITTER_ACCESS_TOKEN_SECRET` | The access token secret for the Twitter API |
| `TWITTER_BEARER_TOKEN` | The bearer token for the Twitter API |
| `TWITTER_HASHTAG` | (optional) Text to be appended to all tweets as a [hashtag](https://help.twitter.com/en/using-twitter/how-to-use-hashtags) |

## License

[MIT License](https://github.com/jnsnkrllive/wx-twitter-bot/blob/master/LICENSE)
