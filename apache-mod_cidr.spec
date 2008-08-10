#Module-Specific definitions
%define mod_name mod_cidr
%define mod_conf B28_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Does hash lookups on the inbound connection source in a network router style
Name:		apache-%{mod_name}
Version:	0.04
Release:	%mkrel 1
Group:		System/Servers
License:	Apache License
URL:		http://www.s5h.net/code/mod-cidr/
Source0:	http://www.s5h.net/code/mod-cidr/%{mod_name}-%{version}.tar.gz
Source1:	%{mod_conf}
Source2:	ipv4.cdb.bz2
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	dos2unix
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod-cidr is a way to perform hash lookups based on the inbound connection
source in a network router style. This module is useful for geo-location or net
block lookups. Information is set in the server headers retrieved from CDB
hash. Lookups are extremely fast since CDB interface is very quick.

%prep

%setup -q -n %{mod_name}
cp %{SOURCE1} .
bzcat %{SOURCE2} > ipv4.cdb

dos2unix -U numtoip.pm

%build

%{_sbindir}/apxs -c %{mod_name}.c cdb.c byte_copy.c seek_set.c error.c \
    uint32_pack.c uint32_unpack.c byte_diff.c cdb_hash.c

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}/var/lib/%{mod_name}

install -m0755 .libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}
install -m0644 ipv4.cdb %{buildroot}/var/lib/%{mod_name}/ipv4.cdb

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README numtoip.pm process_data.pl update.pl
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0644,root,root) %config(noreplace) /var/lib/%{mod_name}/ipv4.cdb
