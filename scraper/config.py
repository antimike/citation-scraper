from pathlib import Path
import yaml

with open("{}/config/wiki_config.yaml".format(Path(__file__).parent.parent), 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
