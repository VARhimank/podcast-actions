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
    parser.add_argument('--json-issue', type=str, required=True)
    parser.add_argument('--api-key', type=str, required=True)
    parser.add_argument('--api-secret', type=str, required=True)
    return parser.parse_args()


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


def create_podcast_yml_file(issue_data, yaml_directory):
    slug = slugify(issue_data['name'])
    podcast_data = {
        'title': issue_data['name'],
        'podcastIndexId': issue_data['podcastIndexId'],
        'tags': issue_data['tags'].split('\n'),
    }
    with open(os.path.join(yaml_directory, f"{podcast_data['slug']}.yml"), 'w') as f:
        yaml.dump(podcast_data, f)


def main():
    args = get_args()
    issue_data = json.loads(args.json_issue)
    create_podcast_yml_file(issue_data, args.yaml_directory)


if __name__ == '__main__':
    main()
