#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /tools/copr/Sanity/copr-cli-basic-operations
#   Description: Tests basic operations of copr using copr-cli.
#   Author: Adam Samalik <asamalik@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2014 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/bin/rhts-environment.sh || exit 1
. /usr/share/beakerlib/beakerlib.sh || exit 1

# Load config settings
HERE=$(dirname "$(realpath "$0")")
source "$HERE/config"


rlJournalStart
    rlPhaseStartSetup
    rlPhaseEnd

    rlPhaseStartTest
        OUTPUT=`mktemp`
        rlRun "copr-cli create --chroot $CHROOT ${NAME_PREFIX}Project10"
        rlRun "copr-cli buildscm ${NAME_PREFIX}Project10 --clone-url http://github.com/clime/example.git"
        rlRun "copr-cli fork ${NAME_PREFIX}Project10 ${NAME_PREFIX}Project10Fork > $OUTPUT"
        rlAssertEquals "Forking project" `grep -r 'Forking project' $OUTPUT |wc -l` 1
        rlAssertEquals "Info about backend data" `grep -r 'Please be aware that it may take a few minutes to duplicate backend data.' $OUTPUT |wc -l` 1

        # attempt to fork into existing project
        OUTPUT=`mktemp`
        rlRun "copr-cli fork ${NAME_PREFIX}Project10 ${NAME_PREFIX}Project10Fork &> $OUTPUT" 1
        rlAssertEquals "Error existing project" `grep -r 'Error: You are about to fork into existing project' $OUTPUT |wc -l` 1
        rlAssertEquals "Use --confirm" `grep -r 'Please use --confirm if you really want to do this' $OUTPUT |wc -l` 1

        # fork into existing project
        OUTPUT=`mktemp`
        rlRun "copr-cli fork ${NAME_PREFIX}Project10 ${NAME_PREFIX}Project10Fork --confirm > $OUTPUT"
        rlAssertEquals "Updating packages" `grep -r 'Updating packages in' $OUTPUT |wc -l` 1

        # give backend some time to fork the data
        echo "sleep 60 seconds to give backend enough time to fork data"
        sleep 60

        # use package from forked project
        rlRun "yes | dnf copr enable ${NAME_PREFIX}Project10Fork $CHROOT"
        rlRun "dnf install -y example"

        # check repo properties
        REPOFILE=$(echo /etc/yum.repos.d/_copr_${NAME_PREFIX}Project10Fork.repo |sed 's/\/TEST/-TEST/g')
        rlAssertEquals "Baseurl should point to fork project" `grep -r "^baseurl=" $REPOFILE |grep ${NAME_PREFIX} |wc -l` 1
        rlAssertEquals "GPG pubkey should point to fork project" `grep -r "^gpgkey=" $REPOFILE |grep ${NAME_PREFIX} |wc -l` 1

        # check whether pubkey.gpg exists
        rlRun "curl -f $(grep "^gpgkey=" ${REPOFILE} |sed 's/^gpgkey=//g')"

        rlRun "yes | dnf copr enable ${NAME_PREFIX}Project10 $CHROOT"
        REPOFILE_SOURCE=$(echo /etc/yum.repos.d/_copr_${NAME_PREFIX}Project10.repo |sed 's/\/TEST/-TEST/g')
        TMP=`mktemp -d`
        rlRun "wget $(grep "^gpgkey=" ${REPOFILE_SOURCE} |sed 's/^gpgkey=//g') -O $TMP/pubkey_source.gpg"
        rlRun "wget $(grep "^gpgkey=" ${REPOFILE} |sed 's/^gpgkey=//g') -O $TMP/pubkey_fork.gpg"
        rlRun "diff $TMP/pubkey_source.gpg $TMP/pubkey_fork.gpg" 1 "simple check that a new key was generated for the forked repo"

        # clean
        rlRun "dnf remove -y example"
        rlRun "yes | dnf copr disable  ${NAME_PREFIX}Project10Fork"

    rlPhaseEnd

    rlPhaseStartCleanup
        rm $TMP/pubkey_fork.gpg
        rm $TMP/pubkey_source.gpg
    rlPhaseEnd
rlJournalPrintText
rlJournalEnd
