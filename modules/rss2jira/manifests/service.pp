# == Class: rss2jira
#
# Configures an rss2jira service.
#
# === Parameters
#
# [*user*]
#   Defines the user that the service will run as.
#   Defaults to 'rss2jira'.
#
# [*db_dir*]
#   Directory that the SQLite database will be stored in.
#   Defaults to '/var/local/rss2jira'.
#
# [*log_dir*]
#   Directory that the rss2jira log will be stored in.
#   Defaults to '/var/log/rss2jira'.
#
class rss2jira::service(
  $user = 'rss2jira',
  $db_dir = '/var/local/rss2jira',
  $log_dir = '/var/log/rss2jira'
){
  Class['rss2jira']
  -> Class['rss2jira::service']

  user { $user:
    ensure => present,
  }

  $rss2jira_conf = '/etc/rss2jira.conf'
  file { $rss2jira_conf:
    ensure  => present,
    content => template("${caller_module_name}/rss2jira.conf"),
    mode    => '0640',
    owner   => $user,
    group   => 'root',
    require => User[$user],
  }

  file { [$log_dir, $db_dir]:
    ensure  => directory,
    owner   => $user,
    mode    => '0755',
    recurse => true,
    require => User[$user],
  }

  $upstart_conf = '/etc/init/rss2jira.conf'
  file { $upstart_conf:
    ensure  => present,
    content => template('rss2jira/upstart.conf'),
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
  }

  file { '/etc/init.d/rss2jira':
    ensure => link,
    target => '/lib/init/upstart-job',
    require => File[$upstart_conf],
  }

  service { 'rss2jira':
    ensure    => running,
    provider  => 'upstart',
    enable    => true,
    require   => [File[$upstart_conf, $rss2jira_conf, $log_dir], User[$user]],
    subscribe => [Package['rss2jira'], File[$upstart_conf, $rss2jira_conf]],
  }
}
