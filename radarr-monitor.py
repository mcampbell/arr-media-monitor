import requests

import argparse
import logging
import json

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s|%(pathname)s:%(lineno)d|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d.%H-%M-%S'
)
log = logging.getLogger(__name__)

def main(args):
    log.setLevel(logging.DEBUG if args.debug else logging.INFO)

    api = 'http://{}:{}/radarr/api/movie/'.format(
        args.host, args.port
    )
    movies_url = '{}?apikey={}'.format(api, args.api_key)
    r = requests.get(movies_url)
    r.raise_for_status()

    movies = r.json()

    for movie in movies:
        dl = movie.get('downloaded')
        monitored = movie.get('monitored')
        path = movie.get('path')
        if dl == monitored:
            movie['monitored'] = not dl  # if downloaded, unset monitored.
            # put url is same as get everything since id is embedded(?)
            log.debug('+: {} -> {}'.format(
                movie.get('path'),
                'unmonitored' if dl else 'monitored'
            ))
            if not args.print_only:
                data = json.dumps(movie)
                log.debug('put-ing to {}, data={}'.format(movies_url, data))
                r = requests.put(movies_url, data=data)
                r.raise_for_status()
        else:
            log.debug('-: {:40s}; {} & {}'.format(
                path.replace('/movies/', ''),
                'downloaded' if dl else 'undownloaded',
                'monitored' if monitored else 'unmonitored',
            ))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Movie un-monitor-or.  Will unmonitor any movies listed as downloaded, and monitor all those not listed as downloaded.'
    )
    parser.add_argument('-D', '--debug',
                        help='Set DEBUG log level.  Default INFO',
                        required=False,
                        action='store_true')
    parser.add_argument('-?', '--print-only',
                        help="print what I'd do, but don't do it",
                        required=False,
                        action='store_true')
    parser.add_argument('--host',
                        help='radarr host',
                        required=False,
                        default='localhost',
                        type=str)
    parser.add_argument('-p', '--port',
                        help='radarr port',
                        required=False,
                        default='7878',
                        type=str)
    parser.add_argument('-a', '--api-key',
                        help='radarr api key',
                        required=True,
                        type=str)

    args = parser.parse_args()

    try:
        main(args)

    except KeyboardInterrupt:
        pass
