#!/bin/bash
# Unofficial bash strict mode
set -euo pipefail
IFS=$'\n\t'

INTERFACE=$1
RT_TABLE=$2
FWMARK=$3
GROUP=$4

# Limpiar las reglas de iptables establecidas
iptables -t mangle -D OUTPUT -m owner --gid-owner $GROUP -j MARK --set-mark $FWMARK
iptables -t nat -D POSTROUTING -m mark --mark $FWMARK -j MASQUERADE

# Limpiar la tabla de rutas
ip route flush table $RT_TABLE

# Limpiar reglas de ip rule
ip rule del fwmark $FWMARK table $RT_TABLE

# Restablecer puerta de enlace por la interfaz objetivo en la tabla de rutas principal
ip route add default dev $INTERFACE

# No se reactiva rp_filter por si otra aplicación lo necesita