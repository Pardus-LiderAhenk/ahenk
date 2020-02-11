#! /bin/bash
#agah = $1
#serife = $2
#kubilay = $3

echo "samba-common samba-common/workgroup string  WORKGROUP" | sudo debconf-set-selections
echo "samba-common samba-common/dhcp boolean false" | sudo debconf-set-selections
echo "samba-common samba-common/do_debconf boolean true" | sudo debconf-set-selections
sudo apt-get -y install samba-common


cat > /root/debconf-krb5.conf << 'EOF'

krb5-config         krb5-config/read_conf               boolean     true
krb5-config         krb5-config/kerberos_servers        string
krb5-config         krb5-config/add_servers             boolean     false
krb5-config         krb5-config/default_realm           string      ENGEREK.LOCAL
krb5-config         krb5-config/add_servers_realm       string      liderahenk.engerek.local
krb5-config         krb5-config/admin_server            string      liderahenk.engerek.local
EOF
export DEBIAN_FRONTEND=noninteractive
cat /root/debconf-krb5.conf | debconf-set-selections
sudo apt-get install krb5-user -y



#sudo apt-get -y install realmd sssd sssd-tools adcli packagekit samba-common-bin samba-libs

