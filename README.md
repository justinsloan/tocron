# ANCHOR
An uptime status and monitoring tool with only 15 pieces of flare.

## Roadmap

### Release 0
 - First packaged release
 - Add/delete nodes
 - De/activate nodes
 - Save/load nodes
 - Node list search
 - ICMP Monitoring w/history
 - Basic fingerprinting
 - Critical indicator

### Release 1
 - Improved fingerprinting
 - `dig` command module

### Release 3
 - Categories for nodes
 - `mtr` route tracing
 - Basic website "defacement" monitoring (if the size of the file changed from last check, character count changes, character-by-character check, sha256 hash, these ideas only work for static sites...)

### Future

#### Health Check
Run essential checks on public domains including DMARC, SPF, SSL validation, DNS propagation, etc.