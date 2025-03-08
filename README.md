<div align="center">

# Stream Notification

Notification of the start of a Twitch Stream for a specified streamer on MacOS

<br>
<br>

</div>

<div align="center">

</div>

>

## Installation

```sh
poetry install
```

## Build

> **Note**
> Set the following in .env

```.env
Client_ID=
Client_Secret=
```

```sh
nuitka --standalone --follow-imports --macos-create-app-bundle --output-dir=build --include-data-dir=src/applescript=applescript --include-data-files=.env=.env setup.py
```

Add the `--macos-app-name` and `--macos-app-icon` options if necessary.

## License

MIT

### Modules

- [inquirerpy](https://github.com/kazhala/InquirerPy)
- [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- [nuitka](https://github.com/Nuitka/Nuitka)
- [aiohttp](https://github.com/aio-libs/aiohttp)
