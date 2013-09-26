class rss2jira {
  package { 'python-pip':
    ensure => present,
  }

  package { 'rss2jira':
    ensure   => latest,
    provider => pip,
    require  => Package['python-pip'],
  }
}
