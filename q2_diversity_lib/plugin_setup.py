# ----------------------------------------------------------------------------
# Copyright (c) 2018-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Plugin, Citations, Bool, Int, Range, Choices, Str,
                           Float, List)
from q2_types.feature_table import (FeatureTable, Frequency, RelativeFrequency,
                                    PresenceAbsence)
from q2_types.tree import Phylogeny, Rooted
from q2_types.sample_data import AlphaDiversity, SampleData
from q2_types.distance_matrix import DistanceMatrix
from unifrac._meta import CONSOLIDATIONS

from . import alpha, beta, __version__, examples

citations = Citations.load('citations.bib', package='q2_diversity_lib')
plugin = Plugin(
    name="diversity-lib",
    version=__version__,
    website="https://github.com/qiime2/q2-diversity-lib",
    short_description="Plugin for computing community diversity.",
    package="q2_diversity_lib",
    description="This QIIME 2 plugin computes individual metrics for "
    " community alpha and beta diversity.",
)

n_jobs_description = (
    "The number of concurrent jobs to use in performing this calculation. "
    "May not exceed the number of available physical cores. If n_jobs = "
    "'auto', one job will be launched for each identified CPU core on the "
    "host."
)

threads_description = (
    "The number of CPU threads to use in performing this calculation. "
    "May not exceed the number of available physical cores. If threads = "
    "'auto', one thread will be created for each identified CPU core on the "
    "host."
)

drop_undef_samples_description = (
    "When calculating some metrics, samples with fewer than a predetermined "
    "number of features produce undefined (NaN) values. If true, affected "
    "samples are dropped from metrics with 'drop_undefined_samples' "
    "implemented. For metrics without a 'drop_undefined_samples' parameter, "
    "this value will be ignored and no samples will be dropped."
)

# ------------------------ alpha-diversity -----------------------
plugin.methods.register_function(
    function=alpha.faith_pd,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency
            | PresenceAbsence],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'threads': Int % Range(1, None) | Str % Choices(['auto'])},
    outputs=[('vector', SampleData[AlphaDiversity])],
    input_descriptions={
        'table': "The feature table containing the samples for which Faith's "
                 "phylogenetic diversity should be computed. Table values "
                 "will be converted to presence/absence.",
        'phylogeny': "Phylogenetic tree containing tip identifiers that "
                     "correspond to the feature identifiers in the table. "
                     "This tree can contain tip ids that are not present in "
                     "the table, but all feature ids in the table must be "
                     "present in this tree."},
    parameter_descriptions={'threads': threads_description},
    output_descriptions={'vector': "Vector containing per-sample values for "
                                   "Faith's Phylogenetic Diversity."},
    name="Faith's Phylogenetic Diversity",
    description="Computes Faith's Phylogenetic Diversity for all samples in "
                "a feature table.",
    examples={'basic': examples.faith_pd_example},
    citations=[citations['faith1992conservation'],
               citations['armstrong2021faithspd']]
)

plugin.methods.register_function(
    function=alpha.observed_features,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency
            | PresenceAbsence]},
    parameters=None,
    outputs=[('vector', SampleData[AlphaDiversity])],
    input_descriptions={'table': "The feature table containing the samples "
                        "for which the number of observed features should be "
                        "calculated. Table values will be converted to "
                        "presence/absence."},
    parameter_descriptions=None,
    output_descriptions={'vector': "Vector containing per-sample counts of "
                                   "observed features."},
    name="Observed Features",
    description="Compute the number of observed features for each sample in a "
                "feature table",
    examples={'basic': examples.observed_features_example}
)

plugin.methods.register_function(
    function=alpha.pielou_evenness,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency]},
    parameters={'drop_undefined_samples': Bool},
    outputs=[('vector', SampleData[AlphaDiversity])],
    input_descriptions={'table': "The feature table containing the samples "
                        "for which Pielou's evenness should be computed."},
    parameter_descriptions={'drop_undefined_samples': "Samples with fewer than"
                            " two observed features produce undefined (NaN) "
                            "values. If true, these samples are dropped "
                            "from the output vector."},
    output_descriptions={'vector': "Vector containing per-sample values "
                                   "for Pielou's Evenness."},
    name="Pielou's Evenness",
    description="Compute Pielou's Evenness for each sample in a "
                "feature table",
    examples={'basic': examples.pielou_evenness_example,
              'dropping undefined samples': examples.pielou_drop_example},
    citations=[citations['pielou1966measurement']]
)

# TODO: Augment citations as needed
plugin.methods.register_function(
    function=alpha.shannon_entropy,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency]},
    parameters={'drop_undefined_samples': Bool},
    outputs=[('vector', SampleData[AlphaDiversity])],
    input_descriptions={'table': "The feature table containing the samples "
                        "for which Shannon's Entropy should be computed."},
    parameter_descriptions={'drop_undefined_samples': "Samples with no "
                            "observed features produce undefined (NaN) values."
                            " If true, these samples are dropped from the "
                            "output vector."},
    output_descriptions={'vector': "Vector containing per-sample values "
                                   "for Shannon's Entropy."},
    name="Shannon's Entropy",
    description="Compute Shannon's Entropy for each sample in a "
                "feature table",
    examples={'basic': examples.shannon_entropy_example,
              'dropping undefined samples': examples.shannon_drop_example},
    citations=[citations['shannon1948communication']]
)


# ------------------------ beta-diversity -----------------------
# TODO: Augment citations as needed
plugin.methods.register_function(
    function=beta.bray_curtis,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency]},
    parameters={'n_jobs': Int % Range(1, None) | Str % Choices(['auto'])},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': "The feature table containing the samples for which "
                 "Bray-Curtis dissimilarity should be computed."},
    parameter_descriptions={'n_jobs': n_jobs_description},
    output_descriptions={
        'distance_matrix': "Distance matrix for Bray-Curtis dissimilarity"},
    name="Bray-Curtis Dissimilarity",
    description="Compute Bray-Curtis dissimilarity for each sample in a "
                "feature table. Note: Frequency and relative frequency data "
                "produce different results unless overall sample sizes are "
                "identical. Please consider the impact on your results if "
                "you use Bray-Curtis with count data that has not been "
                "adjusted (normalized).",
    examples={"run on one core (by default)": examples.bray_curtis_example,
              "to run on n cores, replace 1 here with your preferred integer":
              examples.bray_curtis_n_jobs_example,
              "use 'auto' to run on all of host system's available CPU cores":
              examples.bray_curtis_auto_jobs_example,
              },
    citations=[citations['sorensen1948method']])

# TODO: Augment citations as needed
plugin.methods.register_function(
    function=beta.jaccard,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency
            | PresenceAbsence]},
    parameters={'n_jobs': Int % Range(1, None) | Str % Choices(['auto'])},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': "The feature table containing the samples for which "
                 "Jaccard distance should be computed."},
    parameter_descriptions={'n_jobs': n_jobs_description},
    output_descriptions={
        'distance_matrix': "Distance matrix for Jaccard index"},
    name="Jaccard Distance",
    description="Compute Jaccard distance for each sample "
                "in a feature table. Jaccard is calculated using"
                "presence/absence data. Data of type "
                "FeatureTable[Frequency | Relative Frequency] is reduced"
                "to presence/absence prior to calculation.",
    examples={"run on one core (by default)": examples.jaccard_example,
              "to run on n cores, replace 1 here with your preferred integer":
              examples.jaccard_n_jobs_example,
              "use 'auto' to run on all of host system's available CPU cores":
              examples.jaccard_auto_jobs_example,
              },
    citations=[citations['jaccard1908nouvelles']])


plugin.methods.register_function(
    function=beta.unweighted_unifrac,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency
            | PresenceAbsence],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'threads': Int % Range(1, None) | Str % Choices(['auto']),
                'bypass_tips': Bool},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': "The feature table containing the samples for which "
                 "Unweighted Unifrac should be computed.",
        'phylogeny': "Phylogenetic tree containing tip identifiers that "
                     "correspond to the feature identifiers in the table. "
                     "This tree can contain tip ids that are not present in "
                     "the table, but all feature ids in the table must be "
                     "present in this tree."},
    parameter_descriptions={
        'threads': threads_description,
        'bypass_tips':
            ("In a bifurcating tree, the tips make up about 50% of "
             "the nodes in a tree. By ignoring them, specificity "
             "can be traded for reduced compute time. This has the"
             " effect of collapsing the phylogeny, and is analogous"
             " (in concept) to moving from 99% to 97% OTUs")},
    output_descriptions={'distance_matrix': "Distance matrix for Unweighted "
                         "Unifrac."},
    name="Unweighted Unifrac",
    description="Compute Unweighted Unifrac for each sample in a "
                "feature table",
    examples={"run on one core (by default)": examples.u_u_example,
              "to run on n cores, replace 1 here with your preferred integer":
              examples.u_u_n_threads_example,
              "use 'auto' to run on all of host system's available CPU cores":
              examples.u_u_auto_threads_example,
              "use bypass_tips to trade specificity for reduced compute time":
              examples.u_u_bypass_tips_example,
              },
    citations=[
        citations['lozupone2005unifrac'],
        citations['lozupone2007unifrac'],
        citations['hamady2010unifrac'],
        citations['lozupone2011unifrac'],
        citations['mcdonald2018unifrac']]
)

plugin.methods.register_function(
    function=beta.weighted_unifrac,
    inputs={'table': FeatureTable[Frequency | RelativeFrequency],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'threads': Int % Range(1, None) | Str % Choices(['auto']),
                'bypass_tips': Bool},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': "The feature table containing the samples for which "
                 "Weighted Unifrac should be computed.",
        'phylogeny': "Phylogenetic tree containing tip identifiers that "
                     "correspond to the feature identifiers in the table. "
                     "This tree can contain tip ids that are not present in "
                     "the table, but all feature ids in the table must be "
                     "present in this tree."},
    parameter_descriptions={
        'threads': threads_description,
        'bypass_tips':
            ("In a bifurcating tree, the tips make up about 50% of "
             "the nodes in a tree. By ignoring them, specificity "
             "can be traded for reduced compute time. This has the"
             " effect of collapsing the phylogeny, and is analogous"
             " (in concept) to moving from 99% to 97% OTUs")},
    output_descriptions={'distance_matrix': "Distance matrix for Unweighted "
                         "Unifrac."},
    name="Weighted Unifrac",
    description="Compute Weighted Unifrac for each sample in a "
                "feature table",
    examples={"run on one core (by default)": examples.w_u_example,
              "to run on n cores, replace 1 here with your preferred integer":
              examples.w_u_n_threads_example,
              "use 'auto' to run on all of host system's available CPU cores":
              examples.w_u_auto_threads_example,
              "use bypass_tips to trade specificity for reduced compute time":
              examples.w_u_bypass_tips_example,
              },
    citations=[
        citations['lozupone2005unifrac'],
        citations['lozupone2007unifrac'],
        citations['hamady2010unifrac'],
        citations['lozupone2011unifrac'],
        citations['mcdonald2018unifrac']]
)

# ------------------------ Passthrough Methods ------------------------
plugin.methods.register_function(
    function=alpha.alpha_passthrough,
    inputs={'table': FeatureTable[Frequency]},
    parameters={'metric': Str % Choices(alpha.METRICS['NONPHYLO']['UNIMPL'])},
    outputs=[('vector', SampleData[AlphaDiversity])],
    input_descriptions={'table': "The feature table containing the samples "
                        "for which a selected metric should be computed."},
    parameter_descriptions={'metric':
                            'The alpha diversity metric to be computed.'},
    output_descriptions={'vector': "Vector containing per-sample values "
                                   "for the chosen metric."},
    name="Alpha Passthrough (non-phylogenetic)",
    description="Computes a vector of values (one value for each samples in a "
                "feature table) using the scikit-bio implementation of the "
                "selected alpha diversity metric.",
    examples={'basic': examples.alpha_passthrough_example},
)


plugin.methods.register_function(
    function=beta.beta_passthrough,
    inputs={'table': FeatureTable[Frequency]},
    parameters={'metric': Str % Choices(beta.METRICS['NONPHYLO']['UNIMPL']),
                'pseudocount': Int % Range(1, None),
                'n_jobs': Int % Range(1, None) | Str % Choices(['auto'])},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': 'The feature table containing the samples over which beta '
                 'diversity should be computed.'
    },
    parameter_descriptions={
        'metric': 'The beta diversity metric to be computed.',
        'pseudocount': 'A pseudocount to handle zeros for compositional '
                       'metrics. This is ignored for non-compositional '
                       'metrics.',
        'n_jobs': n_jobs_description
    },
    output_descriptions={'distance_matrix': 'The resulting distance matrix.'},
    name='Beta Passthrough (non-phylogenetic)',
    description="Computes a distance matrix for all pairs of samples in a "
                "feature table using the scikit-bio implementation of the "
                "selected beta diversity metric.",
    examples={"run on one core (by default)":
              examples.beta_passthrough_example,
              "to run on n cores, replace 1 here with your preferred integer":
              examples.beta_passthrough_n_jobs_example,
              "use 'auto' to run on all of host system's available CPU cores":
              examples.beta_passthrough_auto_jobs_example,
              "use 'pseudocount' to manually set a pseudocount for " +
              "compositional metrics":
              examples.beta_passthrough_pseudocount_example,
              },
)


plugin.methods.register_function(
    function=beta.beta_phylogenetic_passthrough,
    inputs={'table': FeatureTable[Frequency],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'metric': Str % Choices(beta.METRICS['PHYLO']['UNIMPL']),
                'threads': Int % Range(1, None) | Str % Choices(['auto']),
                'variance_adjusted': Bool,
                'alpha': Float % Range(0, 1, inclusive_end=True),
                'bypass_tips': Bool},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': 'The feature table containing the samples over which beta '
                 'diversity should be computed.',
        'phylogeny': 'Phylogenetic tree containing tip identifiers that '
                     'correspond to the feature identifiers in the table. '
                     'This tree can contain tip ids that are not present in '
                     'the table, but all feature ids in the table must be '
                     'present in this tree.'
    },
    parameter_descriptions={
        'metric': 'The beta diversity metric to be computed.',
        'threads': threads_description,
        'variance_adjusted': 'Perform variance adjustment based on Chang et '
                             'al. BMC Bioinformatics 2011. Weights distances '
                             'based on the proportion of the relative '
                             'abundance represented between the samples at a'
                             ' given node under evaluation.',
        'alpha': 'This parameter is only used when the choice of metric is '
                 'generalized_unifrac. The value of alpha controls importance'
                 ' of sample proportions. 1.0 is weighted normalized UniFrac.'
                 ' 0.0 is close to unweighted UniFrac, but only if the sample'
                 ' proportions are dichotomized.',
        'bypass_tips': 'In a bifurcating tree, the tips make up about 50% of '
                       'the nodes in a tree. By ignoring them, specificity '
                       'can be traded for reduced compute time. This has the '
                       'effect of collapsing the phylogeny, and is analogous '
                       '(in concept) to moving from 99% to 97% OTUs'
    },
    output_descriptions={'distance_matrix': 'The resulting distance matrix.'},
    name='Beta Phylogenetic Passthrough',
    description="Computes a distance matrix for all pairs of samples in a "
                "feature table using the unifrac implementation of the "
                "selected beta diversity metric.",
    examples={"run on one core (by default)":
              examples.beta_phylo_passthrough_example,
              "to run on n cores, replace 1 here with your preferred integer":
              examples.beta_phylo_passthrough_n_threads_example,
              "use 'auto' to run on all of host system's available CPU cores":
              examples.beta_phylo_passthrough_auto_threads_example,
              "use bypass_tips to trade specificity for reduced compute time":
              examples.beta_phylo_passthrough_bypass_tips_example,
              "variance adjustment":
              examples.beta_phylo_passthrough_variance_adjusted_example,
              "minimal generalized unifrac":
              examples.beta_phylo_passthrough_min_generalized_unifrac_example,
              "generalized unifrac":
              examples.beta_phylo_passthrough_generalized_unifrac_example,
              },
    citations=[
        citations['lozupone2005unifrac'],
        citations['lozupone2007unifrac'],
        citations['hamady2010unifrac'],
        citations['lozupone2011unifrac'],
        citations['mcdonald2018unifrac'],
        citations['chang2011variance'],
        citations['chen2012genUnifrac'],
        citations['sfiligoi2022unifrac']
    ]
)


plugin.methods.register_function(
    function=beta.beta_phylogenetic_meta_passthrough,
    inputs={'tables': List[FeatureTable[Frequency]],
            'phylogenies': List[Phylogeny[Rooted]]},
    parameters={'metric': Str % Choices(beta.METRICS['PHYLO']['UNIMPL']),
                'threads': Int % Range(1, None) | Str % Choices(['auto']),
                'variance_adjusted': Bool,
                'alpha': Float % Range(0, 1, inclusive_end=True),
                'bypass_tips': Bool,
                'weights': List[Float],
                'consolidation': Str % Choices(list(CONSOLIDATIONS))},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'tables': 'The feature tables containing the samples over which beta '
                  'diversity should be computed.',
        'phylogenies': 'Phylogenetic trees containing tip identifiers that '
                       'correspond to the feature identifiers in the table. '
                       'This tree can contain tip ids that are not present in '
                       'the table, but all feature ids in the table must be '
                       'present in this tree.'
    },
    parameter_descriptions={
        'metric': 'The beta diversity metric to be computed.',
        'threads': threads_description,
        'variance_adjusted': 'Perform variance adjustment based on Chang et '
                             'al. BMC Bioinformatics 2011. Weights distances '
                             'based on the proportion of the relative '
                             'abundance represented between the samples at a'
                             ' given node under evaluation.',
        'alpha': 'This parameter is only used when the choice of metric is '
                 'generalized_unifrac. The value of alpha controls importance'
                 ' of sample proportions. 1.0 is weighted normalized UniFrac.'
                 ' 0.0 is close to unweighted UniFrac, but only if the sample'
                 ' proportions are dichotomized.',
        'bypass_tips': 'In a bifurcating tree, the tips make up about 50% of '
                       'the nodes in a tree. By ignoring them, specificity '
                       'can be traded for reduced compute time. This has the '
                       'effect of collapsing the phylogeny, and is analogous '
                       '(in concept) to moving from 99% to 97% OTUs',
        'weights': 'The weight applied to each tree/table pair. This tuple is '
                   'expected to be in index order with tables and phylogenies.'
                   ' Default is to weight each tree/table pair evenly.',
        'consolidation': 'The matrix consolidation method, which determines '
                         'how the individual distance matrices are '
                         'aggregated'
    },
    output_descriptions={'distance_matrix': 'The resulting distance matrix.'},
    name='Beta Phylogenetic Meta Passthrough',
    description="Computes a distance matrix for all pairs of samples in the "
                "set of feature table and phylogeny pairs, using the unifrac "
                "implementation of the selected beta diversity metric.",
    examples={
        "Basic meta unifrac": examples.beta_phylo_meta_passthrough_example,
        "meta with weights": examples.beta_phylo_meta_weights_example,
        "changing the consolidation method":
        examples.beta_phylo_meta_consolidation_example,
    },
    citations=[
        citations['lozupone2005unifrac'],
        citations['lozupone2007unifrac'],
        citations['hamady2010unifrac'],
        citations['lozupone2011unifrac'],
        citations['mcdonald2018unifrac'],
        citations['chang2011variance'],
        citations['chen2012genUnifrac'],
        citations['lozupone2008metaunifrac']
    ]
)
