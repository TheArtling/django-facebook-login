from fabric import task
from invoke import run


@task
def test(c):
    run('py.test -s'
        ' --cov facebook_login'
        ' --cov-report term'
        ' --ds=facebook_login.tests.test_settings')


@task
def test_html(c):
    run('py.test -s'
        ' --cov facebook_login'
        ' --cov-report html'
        ' --ds=facebook_login.tests.test_settings')
