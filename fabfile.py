from fabric import task
from invoke import run


@task
def test(c):
    run('py.test'
        ' --cov facebook_login'
        ' --cov-report term'
        ' --ds=facebook_login.tests.test_settings')
