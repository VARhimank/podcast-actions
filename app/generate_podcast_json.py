import argparse
import hashlib
import json
import os
import time

import requests
import yaml


def get_args():
    parser = argparse.ArgumentParser(description='Generate podcast json')
    parser.add_argument('--yaml-directory', type=str, required=True)
    parser.add_argument('--json-directory', type=str, required=True)
    parser.add_argument('--api-key', type=str, required=True)
    parser.add_argument('--api-secret', type=str, required=True)
    return parser.parse_args()


def get_yaml_files(yaml_directory):
    return [f for f in os.listdir(yaml_directory) if f.endswith('.yml')]


def get_yaml_data(yaml_directory, yaml_files):
    yaml_data = []
    for file in yaml_files:
        with open(os.path.join(yaml_directory, file), 'r') as f:
            yaml_data.append(yaml.safe_load(f))
    return yaml_data


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value


def enrich_data(data, api_key, api_secret, image_directory):
    podcast_index_id = data['podcastIndexID']
    url = f'https://api.podcastindex.org/api/1.0/podcasts/byfeedid?id={podcast_index_id}'
    # we'll need the unix time
    epoch_time = int(time.time())

    # our hash here is the api key + secret + time 
    data_to_hash = api_key + api_secret + str(epoch_time)
    # which is then sha-1'd
    sha_1 = hashlib.sha1(data_to_hash.encode()).hexdigest()

    # now we build our request headers
    headers = {
        'X-Auth-Date': str(epoch_time),
        'X-Auth-Key': api_key,
        'Authorization': sha_1,
        'User-Agent': 'postcast-bot'
    }
    response = requests.get(url, headers=headers)
    status = response.status_code
    print(f"{status=}")
    response_data = response.json()
    data['podcastIndexData'] = response_data
    slug = slugify(response_data['feed']['title'])
    image_url = response_data['feed']['image']
    image_response = requests.get(image_url)
    image_data = image_response.content
    image_file_extension = image_url.split('.')[-1]
    image_filename = f"{slug}.{image_file_extension}"
    with open(os.path.join(image_directory, image_filename), 'wb') as f:
        f.write(image_data)
    enriched_data = {
        'slug': slug,
        'name': response_data['feed']['title'],
        'description': response_data['feed']['description'],
        'feedUrl': response_data['feed']['url'],
        'websiteUrl': response_data['feed']['link'],
        'author': response_data['feed']['author'],
        'episodeCount': response_data['feed']['episodeCount'],
        'categories': response_data['feed']['categories'],
        'tags': data['tags'],
    }
    return enriched_data


def main():
    args = get_args()
    print(f"{args=}")
    yaml_files = get_yaml_files(args.yaml_directory)
    yaml_data = get_yaml_data(args.yaml_directory, yaml_files)
    for data in yaml_data:
        enriched_data = enrich_data(data, args.api_key, args.api_secret, os.path.join(args.json_directory, 'images'))
        print(f"{json.dumps(enriched_data, indent=2)}")
        with open(os.path.join(args.json_directory, f'{enriched_data["slug"]}.json'), 'w') as f:
            f.write(json.dumps(enriched_data, indent=2))


if __name__ == '__main__':
    main()
