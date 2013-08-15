
$srcDir = "/opt/dns_lg" #TODO make this dynamic

$uwsgi_path   = '/usr/local/bin'
$logroot      = '/var/log/nginx'
$nginxconfig  = '/etc/nginx/sites-enabled'
$nginxuser    = 'www-data'
$superviscfg  = '/etc/supervisor/conf.d'
$make_cmd     = 'make'

Exec {
  path      => [ '/bin', '/usr/bin', '/usr/local/bin', '/usr/sbin/' ],
  logoutput => 'on_failure',
  user      => $id,
}

class dns_lg_api_http {

  package { 'www-packages':
    name    => ['nginx', 'wget', 'libssl-dev'],
    ensure  => 'installed',
  }
}

class dns_lg_api_python {

  package { 'packages':
    name    => ['python', 'python-dev', 'swig', 'python-pip', 'lib32z1-dev'],
    ensure  => 'installed',
  }
}

class dns_lg_api_pip {
  include dns_lg_api_python

  exec { 'py-flask':
    command => 'sudo pip install flask',
    user    => root,
    require => Class['dns_lg_api_python'],
  }

  exec { 'py-uwsgi':
    command => 'sudo pip install uwsgi',
    user    => root,
    require => Class['dns_lg_api_python'],
  }
}

class dns_lg_api_ldns {
  include dns_lg_api_python

  $ldns_vers = "1.6.16"

  exec { 'dl-ldns':
    cwd     => $srcDir,
    command => "wget -nc https://www.nlnetlabs.nl/downloads/ldns/ldns-$ldns_vers.tar.gz",
    user    => root,
    creates => "$srcDir/ldns-$ldns_vers.tar.gz",
  }

  exec { 'tar-ldns':
    cwd     => $srcDir,
    command => "tar -xzf ldns-$ldns_vers.tar.gz",
    user    => root,
    require => Exec['dl-ldns'],
    creates => "$srcDir/ldns-$ldns_vers",
  }

  exec { 'cfg-ldns':
    cwd     => "$srcDir/ldns-$ldns_vers",
    command => "$srcDir/ldns-$ldns_vers/configure --with-pyldns",
    user    => root,
    require => [Class['dns_lg_api_python'],Exec['tar-ldns']],
  }

  package { 'pkg-make':
    name    => 'make',
    ensure  => 'installed',
  }

  exec { 'make-ldns':
    cwd     => "$srcDir/ldns-$ldns_vers",
    command => "$make_cmd",
    user    => root,
    require => [Package['pkg-make'], Exec['cfg-ldns']],
    creates => "$srcDir/ldns-$ldns_vers/lib",
  }

  exec { 'install-ldns':
    cwd     => "$srcDir/ldns-$ldns_vers",
    command => "$make_cmd install",
    user    => root,
    require => Exec['make-ldns'],
  }

  package { 'py-ldns':
    name    => 'python-ldns',
    ensure  => 'installed',
    require => Exec['install-ldns'],
  }


}

class dns_lg_api_www {
  include dns_lg_api_http
  include dns_lg_api_pip
  include dns_lg_api_ldns

  $srvname = $fqdn
  $port = '80'
  $serveradmin = 'admin@example.com'
  $appname = "dns_lg_api"
  $approot = $srcDir
  $appfile = 'api'

  file { "$nginxconfig/$appname.conf":
    owner   => "$nginxuser",
    ensure  => 'file',
    content => template("$srcDir/puppet/templates/nginx-server-default.conf.erb"),
    require => Class['dns_lg_api_http'],
  }

  file { "$nginxconfig/default":
    ensure  => 'absent',
    require => Class['dns_lg_api_http'],
  }

  exec { 'nginx-restart':
    command     => "sudo service nginx restart",
    user        => root,
    subscribe   => File["$nginxconfig/$appname.conf"],
    refreshonly => true,
  }

  file { "path-superv1":
    path => "/etc/supervisor",
    ensure => 'directory',
    require => Class['dns_lg_api_pip', 'dns_lg_api_ldns'],
  } 

  file { "path-superv2":
    path => "/etc/supervisor/conf.d",
    ensure => 'directory',
    require => File['path-superv1'],
  } 

  file { "$superviscfg/$appname.conf":
#    owner   => "$nginxuser",
    owner   => root,
    ensure  => 'file',
    content => template("$srcDir/puppet/templates/supervisor.conf.erb"),
    require => File['path-superv2'],
  }

  package { 'pgk-supervisor':
    name    => ['supervisor'],
    ensure  => 'installed',
    require => File["$superviscfg/$appname.conf"],
  }

  exec { 'supervisor-restart':
    command => "supervisorctl restart $appname",
    user    => root,
    require => Package ['pgk-supervisor'],
   }

}

include dns_lg_api_www

