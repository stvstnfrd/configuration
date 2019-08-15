Buildbot
========

Vagrant instance for testing via Buildbot.

The current supported test suites are:
  - quality
  - LMS unit tests
  - CMS unit tests
  - JavaScript unit tests
  - commonlib unit tests

The test suites that have yet to be supported are:
  - LMS acceptance
  - CMS acceptance
  - bok-choy

Manually Restarting Master/Workers
----------------------------------

The Buildbot master and all of the workers are started during provisioning.  If
the VM is halted and restarted, the master and all of the workers must be
restarted manually.

To manually restart the master,

```
vagrant ssh
sudo su buildbot_master
cd /edx/app/buildbot_master
source venv/bin/activate
buildbot start master
```

To manually start a worker,

```
vagrant ssh
sudo su - buildbot_worker
cd /edx/app/buildbot_worker
source venv/bin/activate
buildbot-worker start <worker name>
```

Note that Ansible starts edx-platform workers with the `JSCOVER_JAR` variable
set, which is necessary to generate coverage reports for JavaScript tests.

Configuring Your Host System for X11 Forwarding
-----------------------------------------------

  1. For Mac OS, install [XQuartz](http://xquartz.macosforge.org/). We have
     tested with version 2.7.11. XQuartz installation requires a restart.
  2. On your host machine, run `export VAGRANT_X11=1`.
  3. The X11 display can be set with the `BUILDBOT_MASTER_X11_DISPLAY` variable
     in Ansible. It is `:1` by default.

When running JS tests, you might get an error like this:

```
WebDriverException: Message: 'The browser appears to have exited before we
could connect. The output was: Error: cannot open display: localhost:10.0\n'
```

If you do, you might be experiencing X11 forwarding timeouts. The solution is
is to increate the value for `ForwardX11Timeout` in /etc/ssh\_config to a high
value (`596h` is the maximum). More details about this problem can be found
[here](http://b.kl3in.com/2012/01/x11-display-forwarding-fails-after-some-time/).
