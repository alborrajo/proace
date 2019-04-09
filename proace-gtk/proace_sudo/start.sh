#!/bin/bash
if [ $# -ne 4 ]; then
    echo Usage: $0 interface rt_table fwmark group
    exit 1
fi

INTERFACE=$1
RT_TABLE=$2
FWMARK=$3
GROUP=$4

# Desactivar Reverse Path Filtering
sysctl -w net.ipv4.conf.all.rp_filter=0
sysctl -w net.ipv4.conf.$INTERFACE.rp_filter=0

# Marcar paquetes provinientes de procesos ejecutados con el grupo objetivo
iptables -t mangle -A OUTPUT -m owner --gid-owner $GROUP -j MARK --set-mark $FWMARK

# Regla para dirigir los paquetes marcados a la tabla de rutas especificada
ip rule add fwmark $FWMARK table $RT_TABLE

# En la tabla de rutas: Los paquetes se enrutarán por la puerta de enlace de la interfaz objetivo
ip route add default dev $INTERFACE table $RT_TABLE

# Eliminar puerta de enlace de la interfaz objetivo de la tabla de rutas principal
ip route del default dev $INTERFACE

# Enmascarar la IP de los paquetes marcados con una IP propia de la interfaz objetivo
iptables -t nat -A POSTROUTING -m mark --mark $FWMARK -j MASQUERADE
