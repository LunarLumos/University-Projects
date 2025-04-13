#!/usr/bin/perl
use strict;
use warnings;
use LWP::UserAgent;

my $RED = "\e[31;1m";
my $GREEN = "\e[32;1m";
my $YELLOW = "\e[33;1m";
my $BLUE = "\e[34;1m";
my $MAGENTA = "\e[35;1m";
my $CYAN = "\e[36;1m";
my $RESET = "\e[0m";
my $BRIGHT_GREEN = "\e[1;32m";
my $BRIGHT_RED = "\e[1;31m";
my $BOLD = "\e[1m";
my $UNDERLINE = "\e[4m";
my $BLINK = "\e[5m";

banner();

sub banner {
    print "${CYAN}\n";
    print "    

            ┏┓      •    
            ┃ ┓┏┏┓┏┓┓┏┓┏┏
            ┗┛┗┫┗┫┛┗┗┛┗┫┛
               ┛ ┛     ┛ 
    \n";
    print "${YELLOW}Stellarisys is a smart log detection tool that helps you quickly uncover and understand past events from system logs. It makes monitoring and analyzing your data easier by highlighting important patterns, so you can stay ahead of potential issues.\n";
    print "${RESET}\n";
    print "${BOLD}${MAGENTA}       Created by ${BLINK}${UNDERLINE}Lunar Lumos${RESET}\n";
    print "${CYAN}Department of Cyber Security\n";
    print "${CYAN}Daffodil International University${RESET}\n";
}

my $BOT_TOKEN = "7705705217:AAGzsRTMcSbPp5GOhKFFYJ9vO6AdT4_Nzx8";
my $CHAT_ID = "-4780545288";

sub clean {
    my ($msg) = @_;
    $msg =~ s/\e\[[0-9;]*[mK]//g;
    return $msg;
}

sub s_massage {
    my ($msg) = @_;
    my $clean_msg = clean($msg);

    my $ua = LWP::UserAgent->new;
    my $url = "https://api.telegram.org/bot$BOT_TOKEN/sendMessage";

    my $response = $ua->post(
        $url,
        Content => [
            chat_id => $CHAT_ID,
            text    => $clean_msg,
            parse_mode => 'HTML',
        ]
    );

    if ($response->is_success) {
        print "${BRIGHT_GREEN}[i] Message sent to Telegram.${RESET}\n";
    } else {
        print "${BRIGHT_RED}Failed to send message: " . $response->status_line . "${RESET}\n";
    }
}

package LinkedList;
sub new { bless { head => undef }, shift }

sub add {
    my ($self, $data) = @_;
    $self->{head} = { data => $data, next => $self->{head} };
}

sub show_all {
    my ($self) = @_;
    my $current = $self->{head};
    while ($current) {
        print $current->{data};
        $current = $current->{next};
    }
}

package Stack;
sub new { bless { items => [] }, shift }

sub push { push @{$_[0]->{items}}, $_[1] }

sub pop { pop @{$_[0]->{items}} }

package Queue;
sub new { bless { items => [] }, shift }

sub enqueue { push @{$_[0]->{items}}, $_[1] }

sub dequeue { shift @{$_[0]->{items}} }

sub size { scalar @{$_[0]->{items}} }

package Graph;
sub new { bless { nodes => {} }, shift }

sub add_connection {
    my ($self, $u, $v) = @_;
    $self->{nodes}{$u}{$v} = $self->{nodes}{$v}{$u} = 1;
}

sub print_graph {
    my ($self) = @_;
    while (my ($node, $edges) = each %{$self->{nodes}}) {
        print "$node -> ", join(', ', keys %$edges), "\n";
    }
}

package BST;
sub new { bless { root => undef }, shift }

sub insert {
    my ($self, $value) = @_;
    my $node = \$self->{root};
    while ($$node) {
        $node = $value lt $$node->{value}
              ? \$$node->{left}
              : \$$node->{right};
    }
    $$node = { value => $value, left => undef, right => undef };
}

sub inorder {
    my ($self) = @_;
    my (@stack, $current) = ();
    $current = $self->{root};
    while (@stack || defined $current) {
        if (defined $current) {
            push @stack, $current;
            $current = $current->{left};
        }
        else {
            $current = pop @stack;
            print $current->{value}, "\n";
            $current = $current->{right};
        }
    }
}

package main;

my ($alerts, $events, $requests, $graph, $tree, $last_ip) = 
    (LinkedList->new, Stack->new, Queue->new, Graph->new, BST->new, undef);

my @ATTACK_PATTERNS = (
    { name => 'SQL_INJECTION', pattern => qr/(union\s+select|select\s+from|\@\@version|convert\(int|--\s*$)/i, color => $RED },
    { name => 'XSS', pattern => qr/(<script\b|onerror\s*=|alert\(|document\.cookie)/i, color => $MAGENTA },
    { name => 'PATH_TRAVERSAL', pattern => qr/(?:\.\.\/){2,}|(?:etc|proc)\/[^\s\/]+/, color => $YELLOW },
    { name => 'COMMAND_INJECTION', pattern => qr/(?:;\s*\w+|\|\s*\w+|rm\s+-\w+)/, color => $CYAN }
);

print "${BLUE}================================================  Starting IDS Analysis ===================================================  ${RESET}\n";

while (<STDIN>) {
    chomp;
    my $line = $_;
    my ($ip) = split(' ', $line, 2);
    my $t_found = 0;

    $tree->insert($ip);

    $graph->add_connection($last_ip, $ip) if defined $last_ip;
    $last_ip = $ip;

    foreach my $attack (@ATTACK_PATTERNS) {
        if ($line =~ /$attack->{pattern}/) {
            my $alert = "$attack->{color}ALERT: $attack->{name} detected${RESET}\n$line\n\n";
            print $alert;
            $alerts->add($alert);
            s_massage($alert);
            $t_found = 1;
            last;
        }
    }

    if ($line =~ /login\.php/) {
        $requests->enqueue($line);
        if ($requests->size() > 5) {
            $requests->dequeue();
            my $alert = "${RED}ALERT: BRUTE_FORCE detected from IP: $ip${RESET}\nRequest: $line\n\n";
            print $alert;
            $alerts->add($alert);
            s_massage($alert);
            $t_found = 1;
        }
    }

    print "${GREEN}SAFE:${RESET} $line\n" unless $t_found;
}

print "\n${BLUE}================================================  Summary  ===================================================  ${RESET}\n";
$alerts->show_all();
print "${BLUE}================================================  End of Analysis ===================================================  ${RESET}\n";
