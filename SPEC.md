# ANCHOR
## Administrative Network Command Hub for Operations & Response

## User Stories
**Kori** is the IT Operations Manager for a mid-sized company with 10 geographically dispersed office locations. Each location has a firewall, server, switch, wifi access point, and several computer workstations with VoIP phones at each desk. Kori's primary role is to monitor network performance and make corrections when problems arise. If a server were to go down, for example, Kori needs to be notified quickly so the issue can be investigated and remediated.

When everything looks good on the network, that is, all systems are "green", Kori runs various checks pre-emptively. In addition, there are several tasks that Kori needs to complete on a recurring schedule, such as software updates and automated backups. Most of the tasks are automated, but Kori needs to be able to manually check the results to validate proper performance. In the event that an automated task fails, Kori needs to be able to execute the task on command.

To keep track of all this activity, Kori maintains a list of Nodes and a list of Tasks. Each Task, such as a PING command, only has one associated Node, but each Node can have multiple Tasks.

## Node Attributes
 - id: unique integer value
 - title: arbitrary name of the Node
 - target: the IP address, hostname, or URL of the Node
 - log: admin notes and log of events

## Task Attributes
 - id: unique integer value
 - type: PING, cURL, Traceroute, DNS query, etc.
 - node: ID of the associated Node
 - interval: how often the task should repeat (seconds)
 - log: admin notes and log of events

## Misc. Notes
CAMEO - Command, Administration, Monitoring, Execution & Oversight

ANCHOR - Administrative Network Command Hub for Operations & Response

CILVER - Critical Infrastructure Logistics, Visibility, and Endpoint Response

Card-based interface. Tools to ping, dig, curl, etc. Ability to run arbitrary Python scripts.

Nodes and Tasks

Both nodes and tasks can be saved or temporary

When you add a Node, Anchor will attempt to ping the node automatically. If the response is positive, the timer will be turn on. If the response is negative, the timer will be turned off.