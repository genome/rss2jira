include rss2jira
include rss2jira::service

$exec = '/usr/local/bin/rss2jira-email-report'
$config = '--config /etc/rss2jira.conf'
cron { 'rss2jira-email-report':
  ensure      => absent,
  environment => [
    'REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt',
    'MAILTO=bob@example.com',
  ],
  command     => "${exec} ${config}",
  user        => 'rss2jira',
  hour        => 7,
  minute      => 0,
  weekday     => [ 1, 2, 3, 4, 5 ],
}
