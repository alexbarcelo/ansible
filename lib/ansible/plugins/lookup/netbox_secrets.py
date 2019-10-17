from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: netbox_secrets
    author:
      - Oliver Burkill (@ollybee) <ollybee(at)gmail.com>
      - Alex Barcelo (@alexbarcelo) <alex(at)betarho.net>
    short_description: fetch secrets from Netbox
    description:
      - This lookup returns secrets from a NetBox web application
    requirements:
      - pynetbox (Python API client library for Netbox https://github.com/digitalocean/pynetbox)
    options:
      device:
        description: Device secret_name you want to fetch secrets for
        required: True
      secret_name:
        description: Name of the secret you want to retrieve
        required: True
      host:
        description: URL of Netbox host
        env:
          - secret_name: ANSIBLE_NETBOX_HOST
        required: True
      api_token:
        description: Netbox API token (Read only is good)
        env:
          - secret_name: ANSIBLE_NETBOX_API_TOKEN
        required: True
      private_key_file:
        description: path to private key file for secrets authentication
        type: path
        env:
          - secret_name: ANSIBLE_NETBOX_PRIVATE_KEY_FILE
        required: True
"""

EXAMPLES = """
- secret_name: lookup netbox secret
  debug: mag={{ lookup("netbox_secrets",
                       host="http://localhost:8000",
                       private_key_file=".netbox-private-key.pem",
                       api_token="[token]",
                       device=[inventory_hostname],
                       secret_name="[username]") }}

# If the environment is pre-populated, just use the compact form
- secret_name: lookup another netbox secret
  debug: mag={{ lookup("netbox_secrets", device=[inventory_hostname], secret_name="[username]") }}
"""

RETURN = """
_raw:
  description: value(s) stored in Netbox
"""

import os

HAVE_PYNETBOX = False
try:
    import pynetbox
    HAVE_PYNETBOX = True
except ImportError:
    pass

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def get_envvar_option(self, option):
        """Try to retrieve option first from the environment variables."""
        value = os.getenv("ANSIBLE_NETBOX_%s" % option.upper())
        # Fallback is to the default Ansible plugin get_option method
        return value or self.get_option(option)

    def run(self, terms, variables, **kwargs):

        if not HAVE_PYNETBOX:
            raise AnsibleError("Module pynetbox is not installed")

        self.set_options(direct=kwargs)

        netbox_host = self.get_envvar_option('host')
        token = self.get_envvar_option('api_token')
        private_key_file = self.get_envvar_option('private_key_file')
        secret_name = self.get_envvar_option('secret_name')
        device = self.get_envvar_option('device')

        nb = pynetbox.api(
            netbox_host,
            private_key_file=private_key_file,
            token=token
        )
        conn = nb.secrets.secrets.get(device=device, name=secret_name).plaintext

        return conn
