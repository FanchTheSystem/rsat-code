#!/usr/bin/env perl
# RSATWS.cgi - SOAP server for rsa-tools.

=pod

=head1 DESCRIPTION

Server for RSAT web services.

=cut

use strict;

use SOAP::Transport::HTTP;
use lib '../../perl-scripts/lib/RSAT';


my $server = SOAP::Transport::HTTP::CGI
  -> dispatch_to('RSATWS')
  -> handle;

