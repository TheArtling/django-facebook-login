from fabric import task
from invoke import run

@task
def build(c):
    run('rm -rf build')
    run('rm -rf dist')
    run('python setup.py sdist bdist_wheel')


@task
def release(c):
    run('twine upload --repository-url https://upload.pypi.org/legacy/ dist/*')


@task
def test(c):
    run('py.test -s'
        ' --maxfail=1'
        ' --color=yes'
        ' --cov facebook_login'
        ' --cov-report term'
        ' --cov-report html'
        ' --ds=facebook_login.tests.test_settings')
