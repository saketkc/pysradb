Tutorials & Notebooks
=====================

The notebooks are ordered as a learning path. Start with the Python API,
then move through command-line usage, download planning, search, publication
identifiers, optional metadata enrichment, and BioScience search parsing.

The download notebooks intentionally preview commands and selected rows rather
than fetching large sequencing files during documentation builds.

.. toctree::
   :maxdepth: 1
   :caption: Tutorials

   notebooks/README
   notebooks/01.Python-API_demo.ipynb
   notebooks/02.Commandline_download.ipynb
   notebooks/03.ParallelDownload.ipynb
   notebooks/04.SRA_to_fastq_conda.ipynb
   notebooks/05.Downloading_subsets_of_a_project.ipynb
   notebooks/06.Multiple_SRPs.ipynb
   notebooks/07.Query_Search.ipynb
   notebooks/08.PMC_DOI_Identifiers.ipynb
   notebooks/09.Metadata_enrichment.ipynb
   notebooks/10.Parse_Bioscience_Search.ipynb

You can also view the complete `notebooks directory on GitHub <https://github.com/saketkc/pysradb/tree/develop/notebooks>`_ for additional tutorials and examples.

Potential Future Vignettes
--------------------------

The current notebooks cover the main Python API, command-line downloads,
parallel download planning, subset selection, multi-project metadata,
search, publication identifiers, metadata enrichment, and BioScience search
parsing. Useful follow-up vignettes would be:

* an accession conversion cookbook for GSE, GSM, SRP, SRX, SRS, and SRR mappings;
* GEO matrix download and parsing workflows;
* detailed sample-attribute expansion with ``--desc`` and ``--expand``;
* search summaries that use ``--stats`` and ``--graphs``.
