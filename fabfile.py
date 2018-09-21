from fabric import task
from invoke import run


@task
def test(c):
    run('py.test -s'
        ' --maxfail=1'
        ' --color=yes'
        ' --cov facebook_login'
        ' --cov-report term'
        ' --cov-report html'
        ' --ds=facebook_login.tests.test_settings')
