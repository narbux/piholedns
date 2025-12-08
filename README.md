# Piholedns

This script is used to add CNAME entries to a pihole for DNS resolution. It
can be used in a internal homelab to add new services to the DNS.

## Configuration
Set the environment variables `PIHOLEDNS_API_URL` and `PIHOLEDNS_PASSWORD`.

## Usage

```
usage: piholedns [-h] [--version] domain target

This script is used to add CNAME entries to a pihole for DNS resolution. It can be
used in a internal homelab to add new services to the DNS.

positional arguments:
  domain      new domain to add as CNAME to pihole
  target      target domain where CNAME record should point to

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
```
