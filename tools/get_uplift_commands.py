
from libtbdata.patchanalysis import bug_analysis

BUGS =[1724292,
1722126,
1724577,
1724753,
1720950,
1725581,
1709985,
1725309,
1725705,
1725473,
        ]

CMD_TMPL = "graft_uplift.sh {rev} {approver}"


def get_uplift_revs():
    r = {}
    for bug in BUGS:
        bug_a = bug_analysis(bug, uplift_channel="beta")
        if bug_a["uplift_accepted"]:
            approver = bug_a["uplift_reviewer"]["nick"]
            revs = []
            for patch in bug_a["patches"]:
                if "comm-central" in bug_a["patches"][patch]["url"]:
                    revs.append(patch)
            r[bug] = {"approver": approver, "revs": revs}
    return r


def print_commands(rev_info):
    for bug in rev_info:
        approver = rev_info[bug]['approver']
        revs = rev_info[bug]['revs']
        for rev in revs:
            print("Bug {}".format(bug))
            print(CMD_TMPL.format(rev=rev,approver=approver))


if __name__ == "__main__":
    rev_info = get_uplift_revs()
    print_commands(rev_info)
