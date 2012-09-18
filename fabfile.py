from fabric.api import local


def ut():
    # Runs unit tests
    local("nosetests -i "
            "'^(it|ensure|must|should|specs?|examples?|deve|tests?)' "
            "--with-spec --spec-color"
            )
