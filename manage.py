#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from datetime import datetime
import glob
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'STTsite.settings')
    try:
        recordings_path = 'media/recordings/*.wav'
        for wav_file in glob.glob(recordings_path):
            try:
                os.remove(wav_file)
                print(f"Deleted {wav_file}")
            except OSError as e:
                print(f"Error: {wav_file} : {e.strerror}")
        current_date = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
        with open("record.txt", "w") as file:
            file.write(f"[{current_date} 회의]\n\n")
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
