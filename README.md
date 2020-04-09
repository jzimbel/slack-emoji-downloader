# Slack Emoji Downloader
Mass-downloads a Slack team's custom emoji and aliases.

Aliases are saved as symlinks to the original images to avoid wasting disk space.

Requires [Pipenv](https://pipenv.pypa.io/en/latest/).

Usage:
```sh
cd path/to/slack-emoji-downloader
pipenv install
pipenv run python download.py emoji.json
# wait a potentially very long time
# ...
ls output  # results are saved to the output/ directory
```

**Please note**: I take no responsibility for copyright / intellectual property / trade secrets issues you might get into trouble for by using this script.

## Getting `emoji.json`
1. Open Slack in your browser, with the developer tools open to the network tab on initial load.
2. Click on any request, e.g. `POST conversations.history`.
3. Inspect the request payload's form data for a `token` value. Copy that value.
4. Visit https://api.slack.com/methods/emoji.list/test and paste the token into the "provide your own token" input.
5. Click "Test Method".
6. Save the resulting response as `emoji.json` within the same directory as this README.
