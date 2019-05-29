#!/bin/bash

#Author: <tuncay.colak@tubitak.gov.tr>
#set debconf libnss-ldap and libpam-ldap

ldap_hostname=$1
ldap_base_dn=$2
ldap_user_dn=$3
ldap_user_pwd=$4
ldap_version=$5

echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

## libnss-ldap
echo -e " \
libnss-ldap libnss-ldap/dblogin boolean false
libnss-ldap shared/ldapns/base-dn string $ldap_base_dn
libnss-ldap libnss-ldap/binddn string $ldap_user_dn
libnss-ldap libnss-ldap/dbrootlogin boolean true
libnss-ldap libnss-ldap/override boolean true
libnss-ldap shared/ldapns/ldap-server string $ldap_hostname
libnss-ldap libnss-ldap/confperm boolean false
libnss-ldap libnss-ldap/rootbinddn string $ldap_user_dn
libnss-ldap shared/ldapns/ldap_version select $ldap_version
libnss-ldap libnss-ldap/nsswitch note
libpam-ldap libpam-ldap/dblogin boolean false
libpam-ldap libpam-ldap/dbrootlogin boolean true
libpam-ldap libpam-ldap/override boolean true
libpam-ldap libpam-ldap/pam_password string crypt
libpam-ldap libpam-ldap/rootbinddn string $ldap_user_dn
libpam-ldap libpam-runtime/override boolean false \
" | debconf-set-selections

echo "Name: libnss-ldap/bindpw
Template: libnss-ldap/bindpw
Owners: libnss-ldap, libnss-ldap:amd64

Name: libnss-ldap/rootbindpw
Template: libnss-ldap/rootbindpw
Value:
Owners: libnss-ldap, libnss-ldap:amd64
Flags: seen

Name: libpam-ldap/bindpw
Template: libpam-ldap/bindpw
Owners: libpam-ldap, libpam-ldap:amd64

Name: libpam-ldap/rootbindpw
Template: libpam-ldap/rootbindpw
Value:
Owners: libpam-ldap, libpam-ldap:amd64
Flags: seen
Variables:
 filename = /etc/pam_ldap.secret
 package = libpam-ldap" >> /var/cache/debconf/passwords.dat

echo $ldap_user_pwd > /etc/pam_ldap.secret
apt update
apt-get install libpam-ldap libnss-ldap ldap-utils -y
SUDO_FORCE_REMOVE=yes apt-get install sudo-ldap -y