#!/bin/bash
#set debconf krb5 and samba-common

ad_domain_name=$1
ad_host_name=$2

echo "samba-common samba-common/workgroup string  WORKGROUP" | sudo debconf-set-selections
echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
echo "samba-common samba-common/do_debconf boolean true" | sudo debconf-set-selections
apt-get -y install samba-common


cat > /root/debconf-krb5.conf <<EOF

krb5-config         krb5-config/read_conf               boolean     true
krb5-config         krb5-config/kerberos_servers        string
krb5-config         krb5-config/add_servers             boolean     false
krb5-config         krb5-config/default_realm           string      ${ad_domain_name}
krb5-config         krb5-config/add_servers_realm       string      ${ad_host_name}
krb5-config         krb5-config/admin_server            string      ${ad_host_name}
EOF
export DEBIAN_FRONTEND=noninteractive
cat /root/debconf-krb5.conf | debconf-set-selections
apt-get install krb5-user -y


