# ANCHOR
## Administrative Network Command Hub for Operations & Response

## User Stories
**Kori** is the IT Operations Manager for a mid-sized company with 10 geographically dispersed office locations. Each location has a firewall, server, switch, wifi access point, and several computer workstations with VoIP phones at each desk. Kori's primary role is to monitor network performance and make corrections when problems arise. If a server were to go down, for example, Kori needs to be notified quickly so the issue can be investigated and remediated.

When everything looks good on the network, that is, all systems are "green", Kori runs various checks pre-emptively. In addition, there are several tasks that Kori needs to complete on a recurring schedule, such as software updates and automated backups. Most of the tasks are automated, but Kori needs to be able to manually check the results to validate proper performance. In the event that an automated task fails, Kori needs to be able to execute the task on command.

To keep track of all this activity, Kori maintains a list of Nodes and a list of Tasks. Each Task, such as a PING command, only has one associated Node, but each Node can have multiple Tasks.

## Node Attributes
 - ID: unique integer value
 - Title: arbitrary name of the Node
 - Target: the IP address, hostname, or URL of the Node
 - Log: admin notes and log of events

## Task Attributes
 - ID: unique integer value
 - Type: PING, cURL, Traceroute, DNS query, etc.
 - Node: ID of the associated Node
 - Interval: how often the task should repeat (seconds)

## Misc. Notes
CAMEO - Command, Administration, Monitoring, Execution & Oversight

ANCHOR - Administrative Network Command Hub for Operations & Response

Card-based interface. Tools to ping, dig, curl, etc. Ability to run arbitrary Python scripts.

Nodes and Tasks

Both nodes and tasks can be saved or temporary