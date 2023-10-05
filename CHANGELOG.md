# Wx-Twitter-Bot Changelog

All notable changes to this project should be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## Release 1.3.4 [2023-10-04]
### Enhanced
- Gracefully handle exceptions thrown when retrieving air quality observations

## Release 1.3.3 [2023-10-02]
### Enhanced
- Only save the air quality observation when a new one is received
- Include the observation time when tweeting about air quality

## Release 1.3.2 [2023-10-01]
### Fixed
- Bump `airnowpy` from 2.2.1 to 2.2.2

## Release 1.3.1 [2023-10-01]
### Fixed
- Bump `airnowpy` from 2.2.0 to 2.2.1

## Release 1.3.0 [2023-10-01]
### Added
- The ability to tweet when the air quality level changes

## Release 1.2.6 [2023-08-31]
### Fixed
- Bug with how the Lunar Time task uses time zone

## Release 1.2.5 [2023-08-30]
### Fixed
- Twitter API v2 requires a bearer token to authenticate

## Release 1.2.4 [2023-08-29]
### Fixed
- Log the stack trace when exception is caught while using the Twitter API

## Release 1.2.3 [2023-08-22]
### Fixed
- Bug with how the time zone is setup for use within the Solar Time task

## Release 1.2.2 [2023-08-22]
### Fixed
- Use the application time zone for logging with UTC as backup default

## Release 1.2.1 [2023-08-01]
### Fixed
- Use of Twitter API v2 to create a new tweet

## Release 1.2.0 [2023-07-31]
### Changed
- Updated version of 3rd party library used to interact with the Twitter API

## Release 1.1.0 [2022-09-30]
### Added
- The ability to configure a custom hashtag to append to each tweet

## Release 1.0.0 [2022-09-18]
### Added
- The ability to deploy the application via an image in a docker container
- The ability to specify the path to the application's root directory

## Release 0.2.1 [2022-02-01]
### Fixed
- Bug that prevented lunar informtion from being tweeted

## Release 0.2.0 [2022-01-28]
### Added
- The ability to tweet periodically about moonrise, illumination, and moonset

## Release 0.1.1 [2021-11-28]
### Fixed
- Repeatadly sleep the main thread while keeping it alive to reduce CPU load

## Release 0.1.0 [2020-12-31]
### Added
- The ability to tweet daily about sunrise, solar noon, and sunset
