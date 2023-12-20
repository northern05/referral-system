import os
import sys
def check_logs_folder():
    if not os.path.isdir('logs'):
        os.makedirs(os.path.join('logs'))

    if not os.path.isdir(os.path.join('logs', 'errors')):
        os.mkdir(os.path.join('logs', 'errors'))


check_logs_folder()

from app import app

if __name__ == '__main__':
    app.run(debug=True, port=5010)
