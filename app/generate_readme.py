import argparse
import json
import os
from string import Template


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def get_args():
    parser = argparse.ArgumentParser(description='Update README.md')
    parser.add_argument('--json-directory', type=str, required=True)
    return parser.parse_args()

def get_json_files(json_directory):
    return [f for f in os.listdir(json_directory) if f.endswith('.json')]

def get_json_data(json_directory, json_files):
    json_data = []
    for file in json_files:
        with open(os.path.join(json_directory, file), 'r') as f:
            json_data.append(json.load(f))
    return json_data

def get_podcasts(json_data):
    snippets = []
    for podcast in json_data:
        with open(os.path.join(SCRIPT_DIR, 'templates/partials/podcast.md'), 'r') as f:
            podcast_template = Template(f.read())
        substitution_data = podcast.copy()
        substitution_data['description'] = podcast['description'][:300] + '...'
        substitution_data['tags'] = ', '.join(podcast['tags'])
        snippet = (podcast_template.substitute(substitution_data))
        snippets.append(snippet)
    return snippets


def update_readme(snippets):
    with open(os.path.join(SCRIPT_DIR, 'templates/README.md'), 'r') as f:
        readme_template = Template(f.read())
    with open(os.path.join(SCRIPT_DIR, '../README.md'), 'w') as f:
        f.write(readme_template.substitute({'podcasts': '\n'.join(snippets)}))

    

def main():
    args = get_args()
    json_files = get_json_files(args.json_directory)
    json_data = get_json_data(args.json_directory, json_files)
    podcast_snippets = get_podcasts(json_data)
    update_readme(podcast_snippets)

if __name__ == '__main__':
    main()
