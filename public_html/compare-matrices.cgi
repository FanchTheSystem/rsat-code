#!/usr/bin/perl

############################################ 
## Import lib pat
if ($0 =~ /([^(\/)]+)$/) {
  push (@INC, "$`lib/");
}
use CGI;
use CGI::Carp qw/fatalsToBrowser/;
### redirect error log to a file
BEGIN {
    $ERR_LOG = "/dev/null";
#    $ERR_LOG = "/tmp/RSA_ERROR_LOG.txt";
    use CGI::Carp qw(carpout);
    open (LOG, ">> $ERR_LOG")
	|| die "Unable to redirect log\n";
    carpout(*LOG);
}
require "RSA.lib";
require "RSA2.cgi.lib";
$ENV{RSA_OUTPUT_CONTEXT} = "cgi";

################################################################
## result page header
### Read the CGI query
$query = new CGI;

### print the result page
&RSA_header("compare-matrices result", "results");
&ListParameters() if ($ENV{rsat_echo} >= 2);

#
## Check security issues
&CheckWebInput($query);

## update log file
&UpdateLogFile();


################################################################
## Output paths
local $command = "$ENV{RSAT}/perl-scripts/compare-matrices";

local $output_prefix = "compare-matrices";
local $output_path = &RSAT::util::make_temp_file("",$output_prefix, 1); 
local $output_dir = &ShortFileName($output_path);

## We need to create the output directory before starting
## compare-matrices, since it will generate multiple output files.
system("rm -f $output_path; mkdir -p $output_path"); ## We have to delete the file created by &make_temp_file() to create the directory with same name

################################################################
## command line paramters

## read parameters
local $parameters = " -v 1";

################################################################
## Matrix input format
local $query_matrix_format = lc($query->param('matrix_format'));
($query_matrix_format) = split (/\s+/, $query_matrix_format);
$parameters .= " -format1 ".$query_matrix_format;

################################################################
#### Query matrix file
local $matrix_file = &GetMatrixFile($output_path."/".$output_prefix."_query_matrices.".$query_matrix_format);

$parameters .= " -file1 $matrix_file";

push @result_files, ("Input file",$matrix_file);
push @result_files, ("Result file",$result_file);


# ################################################################
# ## Pseudo-counts CURRENTLY NOT SUPPORTED, SHOULD BE ADDED
# if (&IsReal($query->param('pseudo_counts'))) {
#   $parameters .= " -pseudo ".$query->param('pseudo_counts');
# } else {
#   &FatalError("Pseudo-count should be a real number");
# }
# if ($query->param('pseudo_distribution') eq "equi_pseudo") {
#   $parameters .= " -equi_pseudo ";
# }

################################################################
## Background model method
#&SetBackgroundModel();

################################################################
## bg_pseudo
#if (&IsReal($query->param('bg_pseudo'))) {
#  $parameters .= " -bg_pseudo ".$query->param('bg_pseudo');
#}

################################################################
## Motif database
if ($query->param('db_choice') eq "") {
  ## Upload custom reference motif file
  local $custom_motif_file = $output_path."/custom_motif_file.tf";
  local $upload_custom_motif_file = $query->param('upload_custom_motif_file');
  if ($upload_custom_motif_file) {
    if ($upload_custom_motif_file =~ /\.gz$/) {
      $custom_motif_file .= ".gz";
    }
    local $type = $query->uploadInfo($upload_custom_motif_file)->{'Content-Type'};
    open CUSTOM_MOTIF_FILE, ">$custom_motif_file" ||
      &cgiError("Cannot store reference motif fie file in temp dir.");
    while (<$upload_custom_motif_file>) {
      print CUSTOM_MOTIF_FILE;
    }
    close CUSTOM_MOTIF_FILE;
    $parameters .= " -file2 ".$custom_motif_file;
    $parameters .= " -format2 transfac";
  } else {
    &RSAT::error::FatalError("You did not specify the custom matrix file (for this, you need to click on the Browse button)");
  }
} else {
  my ($mat_db_params, @selected_db) = &GetMatrixDBchoice("mode"=>"radio");
  if (scalar(@selected_db) > 0) {
    $parameters .= $mat_db_params;
  }
}

### other default parmaters
$parameters .= " -strand DR";

################################################################
## Output fields and thresolds
my @supported_output_fields = qw(cor
				 Ncor
				 logoDP
				 logocor
				 Nlogocor
				 Icor
				 NIcor
				 cov
				 dEucl
				 NdEucl
				 NsEucl
				 SSD
				 SW
				 NSW
				 all_metrics
				 matrix_number
				 matrix_id
				 matrix_name
				 matrix_ac
				 width
				 strand
				 direction
				 offset
				 pos
				 consensus
				 match_rank
				 alignments_pairwise
				 alignments_1ton
				);

# my @selected_output_fields = qw(
# 				cor
# 				Ncor
# 				NIcor
# 				NsEucl
# 				SSD
# 				NSW
# 				match_rank
# 				matrix_id
# 				matrix_ac
# 				width
# 				strand
# 				offset
# 				consensus
# 				alignments_1ton);
my @selected_output_fields = ();
my $thresholds = "";
foreach my $field (@supported_output_fields) {
  ## Selected field
  if ($query->param('return_'.$field)) {
    push @selected_output_fields, $field;
  }

  ## Lower threshold
  my $lth = $query->param('lth_'.$field);
  if (&IsReal($lth)) {
    $thresholds .= " -lth ".$field." ".$lth;
  }

  ## Upper threshold
  my $uth = $query->param('uth_'.$field);
  if (&IsReal($uth)) {
    $thresholds .= " -uth ".$field." ".$uth;
  }
}
$parameters .= $thresholds;


## Add some output fields
push @selected_output_fields, qw(
				 matrix_id
				 matrix_name
				 width
				 strand
				 offset
				 consensus
				 alignments_1ton
				);
my $selected_output_fields = join (",", @selected_output_fields);
$parameters .= " -return ".$selected_output_fields;

################################################################
### Output file
$output_file = $output_path."/".$output_prefix.".tab";
$parameters .= " -o ".$output_file;

## Report the full command before executing
&ReportWebCommand($command." ".$parameters);

################################################################
## Display or send result by email
$index_file = $output_path."/".$output_prefix."_index.html";
my $mail_title = join (" ", "[RSAT]", "compare-matrices", &AlphaDate());
if ($query->param('output') =~ /display/i) {
  &EmailTheResult("$command $parameters", "nobody@nowhere", "", title=>$mail_title, index=>$index_file, no_email=>1);
} else {
  &EmailTheResult("$command $parameters", $query->param('user_email'), "", title=>$mail_title,index=>$index_file);
}

################################################################
## Result page footer
print $query->end_html;

exit(0);

