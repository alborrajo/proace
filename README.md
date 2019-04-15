# proace

**pro**cess through interf**ace**

Proace is a Linux utility that makes it easy to route any programs' traffic through an specific interface.

This allows you to, for example, have an internet browser connect to the internet normally while a torrent client connects through a VPN.

## Requirements

- python3

- python-gobject

- pyroute2

- ruamel.yaml

## How to install

1. Clone the repository anywhere

2. Add a new user group to the system.

    ```groupadd proace```

3. Add the new group as a secondary group to any users thay may want to use proace

    ```usermod -G proace YOURUSER```

4. Done!

## How to use

1. Make sure the target interface is up (If you want to route through a VPN, connect to the VPN)

2. Run proace-gtk

    You can provide a configuration file as an argument. If you don't it'll look for one up first on ```./proace.yaml``` and if it doesn't find one there, on ```/etc/proace.yaml```

3. If you haven't already, click the Properties button and change the settings to your liking.

4. Click the play button to set up the routes and tables (Requires root privileges)

5. Run a program through the application launcher or choose one on the file selector

6. PROFIT!

7. Click the stop button to clear the routes and tables when you're done (Optional, requires root privileges)

Keep in mind that if you change VPNs or the network configuration on the target interface changes you'll have to click the play button again.

### Command line usage

You can use the Proace scripts through the command line if you want to:

1. Make sure the target interface is up (If you want to route through a VPN, connect to the VPN)

2. Run proace_sudo/start.sh as root with the following arguments:

    ```proace_sudo/start.sh INTERFACE RT_TABLE FWMARK GROUP```

3. Run any application, command, or process using the target group

    ```sg GROUP "/path/to/bin"```

4. Run proace_sudo/stop.sh as root with the following arguments when you're done (Optional):

    ```proace_sudo/stop.sh INTERFACE RT_TABLE FWMARK GROUP```

As explained in the previous section, if you change VPNs or the network configuration on the target interface changes you'll have to click the play button again.


## How it works

In order to route specific processes' packets, there has to be a way to tell them apart from the other processes' packets. **iptales** ```owner``` module gives us the option to tell them apart by _user_, or _group_. We have chosen the group option.
This way, using an iptables rule, packets sent by processes with _certain group_ are marked.

However, marking is not enough to have said packets routed through an specific interface. Therefore, through an **ip rule**, marked packets _are routed using an specific route table_, which contains the target objective as the gateway.

Forcing packets through said gateway causes a problem: Originally, those packets were routed through another network, which means _they have a source IP from that network_. Luckily it's possible to **mask** the packets with a valid IP for the gateway through a MASQUERADE iptables rule.

This way, packets from certain specific processes', which originally would have been routed through the default gateway, are routed through the target interface gateway, with a corresponding IP. When receiving a response, iptables takes care of that by _unmasking_ the response packets destination IP, allowing the system to take the response to the corresponding process.

The system sees a problem in that since it doesn't expect a packet with a destination IP that doesn't correspond to the target interface IP range, and discards the packet. This is known as **Reverse Path Filtering**, and while it's usually something you'll want enabled, for our use case, it prevents us from fulfilling our objective. Once rp_filter is deactivated, the processes receive their corresponding responses without any problems.