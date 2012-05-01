%define kmod_name		be2net
%define kmod_driver_version	4.0.160r
%define kmod_rpm_release	3
%define kmod_kernel_version	2.6.32-131.12.1.el6
%define kmod_suffix		rhel6u1


%{!?dist: %define dist .el6}

Source0:	%{kmod_name}-%{kmod_driver_version}.tar.bz2
Source1:	%{kmod_name}.files
Source2:	%{kmod_name}.conf
Source3:	find-requires.ksyms
Source4:	kmodtool

%define __find_requires %_sourcedir/find-requires.ksyms

Name:		%{kmod_name}
Version:	%{kmod_driver_version}
Release:	%{kmod_rpm_release}%{?dist}
Summary:	%{kmod_name} kernel module

Group:		System/Kernel
License:	GPLv2
URL:		http://www.kernel.org/
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:	%kernel_module_package_buildreqs
ExclusiveArch:  ppc64

# Uncomment to build "debug" packages
#kernel_module_package -f %{SOURCE1} default debug

# Build only for standard kernel variant(s)
%kernel_module_package -s %{SOURCE4} -f %{SOURCE1} default

%description
%{kmod_name} - driver update

%prep
%setup
set -- *
mkdir source
mv "$@" source/
mkdir obj

%build
for flavor in %flavors_to_build; do
	rm -rf obj/$flavor
	cp -r source obj/$flavor

	# update symvers file if existing
	symvers=source/Module.symvers-%{_target_cpu}
	if [ -e $symvers ]; then
		cp $symvers obj/$flavor/Module.symvers
	fi

	make -C %{kernel_source $flavor} M=$PWD/obj/$flavor
done

%install
export INSTALL_MOD_PATH=$RPM_BUILD_ROOT
export INSTALL_MOD_DIR=extra/%{name}
for flavor in %flavors_to_build ; do
	make -C %{kernel_source $flavor} modules_install \
		M=$PWD/obj/$flavor
	# Cleanup unnecessary kernel-generated module dependency files.
	find $INSTALL_MOD_PATH/lib/modules -iname 'modules.*' -exec rm {} \;
done

install -m 644 -D %{SOURCE2} $RPM_BUILD_ROOT/etc/depmod.d/%{kmod_name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Sep 28 2011 Jiri Olsa <jolsa@redhat.com> 4.0.160r 3
- changing exclusive architecture only to pc64

* Mon Sep 12 2011 Jiri Olsa <jolsa@redhat.com> 4.0.160r 2
- new version update

* Wed Sep 29 2010 Jiri Olsa <jolsa@redhat.com> 2.102.453r 1
- be2net DUP module
