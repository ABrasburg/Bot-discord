apt-get update && apt-get install -y ffmpeg
pipenv install --deploy --ignore-pipfile
pipenv run python bot.py