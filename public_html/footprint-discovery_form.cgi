#!/usr/bin/perl
################################################################
## this cgi script fills the HTML form for the program footprint-discovery
#!/usr/bin/perl
BEGIN {
    if ($0 =~ /([^(\/)]+)$/) {
	push @INC, "$`lib/";
    }
}
use CGI;
use CGI::Carp qw/fatalsToBrowser/;
require "RSA.lib";
require "RSA2.cgi.lib";
use RSAT::Tree;


$ENV{RSA_OUTPUT_CONTEXT} = "cgi";

### Read the CGI query
$query = new CGI;

################################################################
## Initialize parameters


## Output fields
my @output_fields = qw(ident
		       ali_len
		       mismat
		       gap_open
		       e_value
		       bit_sc
		       rank);
my %field_description = ();
$field_description{ident} = "Percentage of identity";
$field_description{ali_len} = "Alignment length";
$field_description{mismat} = "Number of mismatches";
$field_description{gap_open} = "Number of gap openings";
$field_description{e_value} = "E-value";
$field_description{bit_sc} = "Bit score";
$field_description{rank} = "Rank";
#$field_description{s_rank} = "target rank";


################################################################
### default values for filling the form

## Default values for dyad-analysis
%default = ();
&LoadDyadDefault(\%default);

## Default parameters for get-orthologs
&LoadGetOrthoDefault(\%default);

## Other default parameters
$default{dyads_filter} = 'checked';
#$default{bg_model} = 'taxfreq';
$default{bg_model} = 'monad'; ## TEMPORARILY SET TO MONAD BECAUSE I HAVE A BUG WITH TAXFREQ
$default{leaders} = '';
$default{uth_rank} = 50;
$default{to_matrix} = 1;
$default{multi_genes} = "separately";

### replace defaults by parameters from the cgi call, if defined
foreach $key (keys %default) {
  if ($query->param($key)) {
    $default{$key} = $query->param($key);
  }
}

################################################################
### print the form ###


## Header
&RSA_header("footprint-discovery", "form");
print "<CENTER>";
print "Given one or several genes from a query organism, collect all orthologous genes for a given taxonomical level <br>and discover conserved elements in their promoters.<br>\n";
print "(Program developed by <A href='mailto:rekins\@bigre.ulb.ac.be'>Rekin's Janky</A>\n";
print "and <a href='mailto:Jacques.van-Helden\@univ-amu.fr'>Jacques van Helden</A>).\n";
print "<br>Reference: <a target='_blank' href=\"http://www.biomedcentral.com/1471-2105/9/37\">Janky & van Helden, BMC Bioinformatics 2008, 9:37.</a>";
print "</CENTER>";
print "<BLOCKQUOTE>\n";

&ListDefaultParameters() if ($ENV{rsat_echo} >= 2);

################################################################
## Display the form only if it is relevant for the organisms supported
## on this RSAT instance.
&check_phylo_tools();

################################################################
## Form header

print $query->start_multipart_form(-action=>"footprint-discovery.cgi");

## Options for the selection of orthologs
print "<hr>";
&PrintOrthoSelectionSection();

## Use predicted leader genes
print "<br>";
print $query->checkbox(-name=>'leaders',
		       -checked=>$default{leaders},
		       -label=>'');
print "<A HREF='help.footprint-discovery.html#leader'><B>\n";
print "predict operon leader genes";
print "</B></A>\n";

## Analyze each gene separately or group genes
print "<br>";
print "<b><a href='help.footprint-discovery.html#multi_genes'>Treat genes</A>&nbsp;</b>\n";
print $query->popup_menu(-name=>'multi_genes',
			 -Values=>['separately',
				   'as a cluster'],
			 -default=>$default{multi_genes});

################################################################
#### Footprint-discovery-specific options
print "<hr>";
print "<p><b>Options for <i>dyad-analysis</i></b></p>";

print "<ul>";

### filtering dyads
print $query->checkbox(-name=>'dyads_filter',
		       -checked=>$default{dyads_filter},
		       -label=>'');
print "<a href='help.footprint-discovery.html#filtering'><b>\n";
print "dyad filtering</b></a>\n";
print "(only accept dyads having at least one occurrence in the promoter of the query gene)";

## Ackground model
print "<br>";
print "<b><a href='help.footprint-discovery.html#bg_model'>Background model</A>&nbsp;</b>\n";
print $query->popup_menu(-name=>'bg_model',
			 -Values=>['taxfreq', ## taxon-wise background model (taxfreq)
				   'monads'], ## background model estimated from the input sequence set
			 -default=>$default{bg_model});


################################################################
## Print dyad return fields
&PrintDyadReturnFields(no_matrix=>1);


# #### Convert patterns to matrix
# print $query->checkbox(-name=>'to_matrix',
# 		       -checked=>$default{to_matrix},
# 		       -label=>'');
# print "&nbsp;Convert assembled patterns to Position-Specific Scoring Matrices";
# print "<BR>";

print "</ul>";

################################################################
## Select output mode. Email is preferred since footprint discovery
## may take a while.
print "<hr>";
&SelectOutput('email');

################################################################
### action buttons
print "<UL><UL><TABLE class = 'formbutton'>\n";
print "<TR VALIGN=MIDDLE>\n";
print "<TD>", $query->submit(-label=>"GO"), "</TD>\n";
print "<TD>", $query->reset, "</TD>\n";
print $query->end_form;

################################################################
### data for the demo 
#$demo_queries .= "recA\n";
#$demo_queries .= "uvrB\n";

print "<script>
function setDemo(){
    \$('#reset').trigger('click');
    \$('#queries').val('lexA');
    
    \$('#organism').val('Escherichia_coli_GCF_000005845.2_ASM584v2');
    \$('#organism_name').val('Escherichia coli GCF_000005845.2 ASM584v2');
    \$('#taxon_name').val('Gammaproteobacteria');
    \$('#taxon').val('Gammaproteobacteria');
    unique_taxon.value = 'genus';
}
</script>";

print '<TD><B>
<button type="button" onclick="setDemo()">DEMO</button>
</B></TD>';


#print "<TD><B>";
#print $query->hidden(-name=>'queries',-default=>$demo_queries);
#print $query->hidden(-name=>'organism',-default=>"Escherichia_coli_GCF_000005845.2_ASM584v2");
#print $query->hidden(-name=>'taxon',-default=>"Gammaproteobacteria");
#print $query->hidden(-name=>'unique_taxon',-default=>"genus");
#print $query->submit(-label=>"DEMO");
#print "</B></TD>\n";
#print $query->end_form;


print "<TD><B><A HREF='help.footprint-discovery.html'>MANUAL</A></B></TD>\n";
#print "<TD><B><A HREF='tutorials/tut_footprint-discovery.html'>TUTORIAL</A></B></TD>\n";
print "<TD><B><A HREF='mailto:Jacques.van-Helden\@univ-amu.fr'>MAIL</A></B></TD>\n";
print "</TR></TABLE></UL></UL>\n";

print "</BLOCKQUOTE>\n";

print "<hr class=solid>";

print $query->end_html;

exit(0);

