import semantic_version as semver, sys


pre_release_snapshot_list = ["test"]
pre_release_release_list = ["rc", "beta", "alpha"]


# 1.0.0-test.3
# 1.0.0-alpha.1
# 1.0.0-beta.2
# 1.0.0-rc.1
# 1.0.0


def create_file(filename, content):
    file = open(filename, "w+")
    file.write(content)
    file.close()


if __name__ == '__main__':
    # get all arguments
    args = sys.argv

    # first argument is the tag name, it represents the version number.
    tag = args[1]
    v = semver.Version(tag)

    if len(v.prerelease) == 0:
        # it's a RELEASE version
        create_file("release.tmp", "RELEASE")
        create_file("repo_name.tmp", "pypi")

    elif v.prerelease[0] in pre_release_release_list:
        # it's a pre-release RELEASE verison
        create_file("release.tmp", "RELEASE")
        create_file("repo_name.tmp", "pypi")

    elif v.prerelease[0] in pre_release_snapshot_list:
        # it's a pre-release SNAPSHOT verison
        create_file("release.tmp", "SNAPSHOT")
        create_file("repo_name.tmp", "pypi-snapshot")

    else:
        # it's a non managed prelease type
        print(tag + " is not a manged prelease type -> " + str(pre_release_snapshot_list) + " or " + str(pre_release_release_list))
        exit(1)

    try:
        print("export PRE_RELEASE='{}'".format(v.prerelease[0]))
    except IndexError:
        print("export PRE_RELEASE='{}'".format(""))

    exit(0)


