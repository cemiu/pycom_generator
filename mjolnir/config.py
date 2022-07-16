
# defaults:
config = {
    '_debug': False,
    'email': None,  # for uniprot request header
    'enable_compression': False,  # todo change to True later
    'commit_frequency': 500,
}


def load_config(config_file):
    """Loads config from a file."""
    pass


__all__ = ['config']
