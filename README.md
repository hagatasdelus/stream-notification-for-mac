<div align="center">

# Stream Notification

Notification of the start of a Twitch Stream for a specified streamer on MacOS

<br>
<br>

</div>

<div align="center">

</div>

## Installation

```sh
git clone https://github.com/hagatasdelus/stream-notification-for-mac.git
```

Install project packages using Poetry.

```sh
poetry install
```

> **Notes**
> If the version of Poetry is 2.x, do the following

```sh
poetry self add poetry-plugin-shell
```

## Build

> **Note**
> Set the following in .env

```.env
Client_ID=your_client_id
Client_Secret=your_client_secret
```

### Packaging the application

Entering the virtual environment

```sh
poetry shell
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
- [aiohttp](https://github.com/aio-libs/aiohttp)
- [nuitka](https://github.com/Nuitka/Nuitka)
