#!/usr/bin/perl
use strict;
use warnings;
use LWP::UserAgent;

# Color codes for terminal output
my $RED = "\e[31;1m";           # Red color for alerts
my $GREEN = "\e[32;1m";         # Green color for safe messages
my $YELLOW = "\e[33;1m";        # Yellow color for warnings
my $BLUE = "\e[34;1m";          # Blue color for informational messages
my $MAGENTA = "\e[35;1m";       # Magenta color for specific patterns
my $CYAN = "\e[36;1m";          # Cyan color for specific patterns
my $RESET = "\e[0m";            # Reset the color to default
my $BRIGHT_GREEN = "\e[1;32m";  # Bright green for successful actions
my $BRIGHT_RED = "\e[1;31m";    # Bright red for errors
my $BOLD = "\e[1m";             # Bold text
my $UNDERLINE = "\e[4m";        # Underlined text
my $BLINK = "\e[5m";            # Blinking text for emphasis

# Display a banner with the script's title and version
banner();

# Function to display the banner (without returning a value)
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

# Telegram Bot credentials (replace with your bot token and chat ID)
my $BOT_TOKEN = "7705705217:AAGzsRTMcSbPp5GOhKFFYJ9vO6AdT4_Nzx8";
my $CHAT_ID = "-4780545288";  # Your chat ID

# Function to clean any unwanted characters or escape sequences from the message
sub clean {
    my ($msg) = @_;
    $msg =~ s/\e\[[0-9;]*[mK]//g;  # Remove color codes
    return $msg;
}

# Function to send a message to a Telegram channel or user
sub s_massage {
    my ($msg) = @_;
    my $clean_msg = clean($msg);  # Clean the message before sending
    
    my $ua = LWP::UserAgent->new;  # Create a new user agent for HTTP requests
    my $url = "https://api.telegram.org/bot$BOT_TOKEN/sendMessage";  # Telegram API URL
    
    # Make a POST request to send the message
    my $response = $ua->post(
        $url,
        Content => [
            chat_id => $CHAT_ID,    # Target chat ID
            text    => $clean_msg,   # Message content
            parse_mode => 'HTML',    # Enable HTML formatting in messages
        ]
    );

    # Check if the message was sent successfully
    if ($response->is_success) {
        print "${BRIGHT_GREEN}[i] Message sent to Telegram.${RESET}\n";
    } else {
        print "${BRIGHT_RED}Failed to send message: " . $response->status_line . "${RESET}\n";
    }
}

# LinkedList class to store alerts
package LinkedList;
sub new { bless { head => undef }, shift }

# Add a new item to the list
sub add {
    my ($self, $data) = @_;
    $self->{head} = { data => $data, next => $self->{head} };  # Add to the head
}

# Show all items in the list
sub show_all {
    my ($self) = @_;
    my $current = $self->{head};
    while ($current) {
        print $current->{data};  # Print each item
        $current = $current->{next};  # Move to the next item
    }
}

# Stack class to hold events
package Stack;
sub new { bless { items => [] }, shift }

# Push an item onto the stack
sub push { push @{$_[0]->{items}}, $_[1] }

# Pop an item from the stack
sub pop { pop @{$_[0]->{items}} }

# Queue class to manage requests
package Queue;
sub new { bless { items => [] }, shift }

# Enqueue an item to the queue
sub enqueue { push @{$_[0]->{items}}, $_[1] }

# Dequeue an item from the queue
sub dequeue { shift @{$_[0]->{items}} }

# Get the size of the queue
sub size { scalar @{$_[0]->{items}} }

# Graph class to store IP connections
package Graph;
sub new { bless { nodes => {} }, shift }

# Add a connection between two nodes (IP addresses)
sub add_connection {
    my ($self, $u, $v) = @_;
    $self->{nodes}{$u}{$v} = $self->{nodes}{$v}{$u} = 1;  # Bidirectional connection
}

# Show all connections in the graph
sub print_graph {
    my ($self) = @_;
    while (my ($node, $edges) = each %{$self->{nodes}}) {
        print "$node -> ", join(', ', keys %$edges), "\n";  # Print each node and its connections
    }
}

# Binary Search Tree (BST) class for sorting IP addresses
package BST;
sub new { bless { root => undef }, shift }

# Insert a new value into the BST
sub insert {
    my ($self, $value) = @_;
    my $node = \$self->{root};
    while ($$node) {
        $node = $value lt $$node->{value} 
              ? \$$node->{left}  # Move left if value is less
              : \$$node->{right};  # Move right if value is greater
    }
    $$node = { value => $value, left => undef, right => undef };  # Insert the value
}

# Perform an inorder traversal of the BST and print the sorted values
sub inorder {
    my ($self) = @_;
    my (@stack, $current) = ();
    $current = $self->{root};
    while (@stack || defined $current) {
        if (defined $current) {
            push @stack, $current;  # Traverse left subtree
            $current = $current->{left};
        }
        else {
            $current = pop @stack;  # Visit the current node
            print $current->{value}, "\n";  # Print the value
            $current = $current->{right};  # Traverse right subtree
        }
    }
}

# Main package where the program logic is executed
package main;

# Initialize data structures
my ($alerts, $events, $requests, $graph, $tree, $last_ip) = 
    (LinkedList->new, Stack->new, Queue->new, Graph->new, BST->new, undef);

# Define attack patterns with regular expressions
my @ATTACK_PATTERNS = (
    { name => 'SQL_INJECTION', pattern => qr/(union\s+select|select\s+from|\@\@version|convert\(int|--\s*$)/i, color => $RED },
    { name => 'XSS', pattern => qr/(<script\b|onerror\s*=|alert\(|document\.cookie)/i, color => $MAGENTA },
    { name => 'PATH_TRAVERSAL', pattern => qr/(?:\.\.\/){2,}|(?:etc|proc)\/[^\s\/]+/, color => $YELLOW },
    { name => 'COMMAND_INJECTION', pattern => qr/(?:;\s*\w+|\|\s*\w+|rm\s+-\w+)/, color => $CYAN }
);

# Display start of analysis
print "${BLUE}================================================  Starting IDS Analysis ===================================================  ${RESET}\n";

# Process each line from the input
while (<STDIN>) {
    chomp;
    my $line = $_;
    my ($ip) = split(' ', $line, 2);  # Extract IP address from the input line
    my $t_found = 0;

    # Insert IP into the Binary Search Tree
    $tree->insert($ip);

    # Add connection to the graph if the previous IP exists
    $graph->add_connection($last_ip, $ip) if defined $last_ip;
    $last_ip = $ip;

    # Check for attack patterns in the line
    foreach my $attack (@ATTACK_PATTERNS) {
        if ($line =~ /$attack->{pattern}/) {
            # Alert if an attack pattern is detected
            my $alert = "$attack->{color}ALERT: $attack->{name} detected${RESET}\n$line\n\n";
            print $alert;  # Print the alert to the console
            $alerts->add($alert);  # Add the alert to the LinkedList
            s_massage($alert);  # Send the alert to Telegram
            $t_found = 1;
            last;
        }
    }

    # Check if the line contains a login attempt (brute-force detection)
    if ($line =~ /login\.php/) {
        $requests->enqueue($line);
        if ($requests->size() > 5) {
            $requests->dequeue();  # Remove the oldest request
            my $alert = "${RED}ALERT: BRUTE_FORCE detected from IP: $ip${RESET}\nRequest: $line\n\n";
            print $alert;  # Print the brute-force alert with IP and request
            $alerts->add($alert);  # Add to the alerts list
            s_massage($alert);  # Send the alert to Telegram
            $t_found = 1;
        }
    }

    # Print a safe message if no threat is found
    print "${GREEN}SAFE:${RESET} $line\n" unless $t_found;
}

# Print a summary of the analysis results
print "\n${BLUE}================================================  Summary  ===================================================  ${RESET}\n";
$alerts->show_all();
print "${BLUE}================================================  End of Analysis ===================================================  ${RESET}\n";
