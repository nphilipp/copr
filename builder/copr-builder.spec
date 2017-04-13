%global		confdir %_sysconfdir/%name

Name:		copr-builder
Version:	0
Release:	10%{?dist}
Summary:	Build package from copr dist-git

License:	GPLv2+
URL:		https://pagure.io/copr/copr

Source0:	copr-builder
Source1:	LICENSE
Source3:	README

# Those could be dropped, but still we keep them at least for reference (those
# files are not aimed to be used by production builders).  The real
# configuration will be copied on builder via backend's VM spin-up playbook.
Source2:	fedora-copr.conf
Source4:	fedora-copr-dev.conf
Source5:	rhcopr.conf
Source6:	rhcopr-stg.conf
Source7:	rhcopr-dev.conf

Requires:	crudini
Requires:	copr-cli
Requires:	mock
Requires:	rpkg
Requires:	expect
Requires:	util-linux
Requires:	sed

BuildArch:	noarch

%description
Knowing copr name, package name and dist-git git hash, build automatically the
package locally in mock.


%prep
%setup -q -c -T
cp %SOURCE1 .
cp %SOURCE3 .


%build


%install
install -d %buildroot%_bindir
install -d %buildroot%_sysconfdir/copr-builder
install -d %buildroot%_sharedstatedir/copr-builder

install -p -m 755 %SOURCE0 %buildroot%_bindir
install -p -m 644 %SOURCE2 %buildroot%confdir
install -p -m 644 %SOURCE4 %buildroot%confdir
install -p -m 644 %SOURCE5 %buildroot%confdir
install -p -m 644 %SOURCE6 %buildroot%confdir
install -p -m 644 %SOURCE7 %buildroot%confdir


%files
%doc LICENSE README
%_bindir/copr-builder
%confdir
%dir %attr(0775, root, mock) %_sharedstatedir/copr-builder


%changelog
* Thu Apr 13 2017 Pavel Raiskup <praiskup@redhat.com> - 0-10
- add --mock-opts option

* Tue Apr 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0-9
- more lively logs with sed filtering

* Tue Apr 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0-8
- touch 'success' file

* Tue Apr 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0-7
- distribute non-default configuration
- fix --chroot option

* Tue Apr 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0-6
- add timeout option

* Tue Apr 04 2017 Pavel Raiskup <praiskup@redhat.com> - 0-5
- changes needed after copr PR 44

* Mon Mar 27 2017 Pavel Raiskup <praiskup@redhat.com> - 0-4
- several TODOs implemented

* Mon Mar 20 2017 Pavel Raiskup <praiskup@redhat.com> - 0-3
- filter both stderr and stdout through 'col -b' for sub-commands

* Mon Mar 20 2017 Pavel Raiskup <praiskup@redhat.com> - 0-2
- a bit nicer live logs in copr

* Sun Mar 19 2017 Pavel Raiskup <praiskup@redhat.com> - 0-1
- package also README

* Sun Mar 19 2017 Pavel Raiskup <praiskup@redhat.com> - 0-0
- Initial commit
