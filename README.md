# RESCRIPt Tutorial
This repository serves as an introduction on how to use RESCRIPt (specifically to create a custom reference genome using NCBI).

### Acknowledgements 
This tutorial is based on other publicaly available workflows & the RESCRIPt GitHub page, many thanks for their work: 
* [RESCRIPt](https://github.com/bokulich-lab/RESCRIPt.git)
* [Using RESCRIPt to compile sequence databases and taxonomy classifiers from NCBI Genbank](https://forum.qiime2.org/t/using-rescript-to-compile-sequence-databases-and-taxonomy-classifiers-from-ncbi-genbank/15947)

## Download RESCRIPt

In order to use RESCRIPt, you need to dowload QIIME 2. QIIME can be downloaded in many ways depending on the machine that you are working on. See the documentation for installing [QIIME 2](https://docs.qiime2.org/2024.10/install/).

I choose to natively install QIIME through Miniconda. This required first [Installing Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) and then creating a conda enviorment for QIIME (my enviorment was named: qiime2-amplicon-2024.10). The version that I downloaded was QIIME 2 Amplicon Distribution for macOS (Apple Silicon). 

After QIIME was installed, the next step was installing RESCRIPt. The command that I used to install RESCRIPt was: 

`pip install git+https://github.com/bokulich-lab/RESCRIPt.git`

NOTE: Before you do any work, make sure to activate the qiime2 conda envirorment: 

`conda activate qiime2-amplicon-2024.10`

# How-To: Create a Refrence Database 

To curate your own refrence database, there are many ways to retrevie refrence sequence data. Some potential databases that you can directly grab data from include: 
* SILVA database (`get-silva-data`)
* NCBI Genbank data (`get-ncbi-data`)
* GTDB data (`get-gtdb-data`)
* UNITE data (`get-unite-data`)

In this tutorial, I am using the the get-ncbi-data functionality to test making a refrence database, and this is the platform I am most familiar and comfortable with. I am also focusing on fish refrence genomes, and it is the most applicable to my work. 

### 1. Download Fish Sequence Data from NCBI with RESCRIPt
* Use `get-ncbi-data` to retrieve fish sequences by specifying an appropriate query.
* This query is similar to how you would serach on the NCBI website. I found it helpful to use the website to specify what I was looking for and on the side it shows “Search Details” giving the specific format for the query search, which is what I used in the code below
  * <img width="492" alt="Screenshot 2024-11-10 at 10 25 36 PM" src="https://github.com/user-attachments/assets/7e088faa-b252-424f-913d-bf4cf19290e1">
* To focus on a subset of fish data, use either a BioProject ID associated with fish studies or a taxonomic query (e.g., specific to Actinopterygii, the class of ray-finned fishes which are most common in freshwater ecosystems).
  * NOTE: A broader search such as "Actinopterygii" was taking too long, and too computationaly expensive for my machine, so I decided for the sake of time and this project to reduce the number of sequences I was using to include only complete genomes.
* `qiime rescript get-ncbi-data --p-query 'Actinopterygii[Organism] AND "complete genome"[Title]' --o-sequences fish-refseqs-unfiltered.qza --o-taxonomy fish-refseqs-taxonomy-unfiltered.qza --p-n-jobs 3`
    * --p-query: Query search applied on the NCBI Nucleotide database. ‘Actinopterygii[Organism] AND "complete genome"[Title]' looks for complete genomes in the taxon Actinopterygii
    * --o-sequences: Outputs FeatureData[Sequence]; sequences from the NCBI Nucleotide database (fish-refseqs-unfiltered.qza)
    * --o-taxonomy: Outputs FeatureData[Taxonomy]; taxonomies from the NCBI Taxonomy database (refseqs-taxonomy-unfiltered.qza)
    * p-n-jobs: Number of concurrent download connections, more is faster until you run out of bandwidth; default = 1. 
### 2. Filter Sequences by Length
* Fish reference sequences might vary in length, and you can filter out shorter sequences that may not be as useful for classification. Set a minimum and maximum length appropriate for the target gene (e.g., COI or 12S rRNA), or in my case I chose to do whole genomes so I set lengths accordingly.
* `qiime rescript filter-seqs-length-by-taxon --i-sequences fish-refseqs-unfiltered.qza --i-taxonomy fish-refseqs-taxonomy-unfiltered.qza --p-labels Actinopterygii --p-min-lens 10000 --p-max-lens 20000 --o-filtered-seqs fish-refseqs.qza --o-discarded-seqs fish-refseqs-tooshortorlong.qza`
    * qiime rescript filter-seqs-length-by-taxon: RESCRIPt plugin in QIIME 2 to filter sequences by length, based on taxonomic information
    * --i-sequences fish-refseqs-unfiltered.qza: Specifies the input sequence file (fish-refseqs-unfiltered.qza), which is in QIIME Artifact format (.qza). This file contains the unfiltered set of reference sequences for fish (which we created in step 1).
    * --i-taxonomy fish-refseqs-taxonomy-unfiltered.qza: Specifies the input taxonomy file (fish-refseqs-taxonomy-unfiltered.qza), which associates taxonomic classifications with the sequences in the unfiltered dataset.
    * --p-labels Actinopterygii: This parameter (--p-labels) limits filtering to sequences labeled with this taxon. Only sequences classified under Actinopterygii (ray-finned fishes) will be filtered based on length.
    * --p-min-lens 10000: Sets the maximum sequence length to 20,000 base pairs. Any sequences longer than this will also be discarded.
    * --p-max-lens 20000: Sets the maximum sequence length to 20,000 base pairs. Any sequences longer than this will also be discarded.
    * --o-filtered-seqs fish-refseqs.qza: Specifies the output file for the filtered sequences (fish-refseqs.qza). This file will contain only the sequences that fall within the specified length range (10,000–20,000 bp) for Actinopterygii.
    * --o-discarded-seqs fish-refseqs-tooshortorlong.qza: Specifies the output file for sequences that were discarded (fish-refseqs-tooshortorlong.qza). This file will contain sequences that were either shorter than 10,000 bp or longer than 20,000 bp.
### 3. Filter the Taxonomy File
* Ensure that the taxonomies align with your filtered sequence data by filtering out any taxonomies not in your filtered dataset.
* `qiime rescript filter-taxa --i-taxonomy fish-refseqs-taxonomy-unfiltered.qza --m-ids-to-keep-file fish-refseqs.qza --o-filtered-taxonomy fish-refseqs-taxonomy.qza`
    * qiime rescript filter-taxa: RESCRIPt plugin for QIIME 2. It filters a taxonomy file to keep only the taxonomies associated with a specific set of sequence IDs.
    * --i-taxonomy fish-refseqs-taxonomy-unfiltered.qza: Specifies the input taxonomy file (fish-refseqs-taxonomy-unfiltered.qza) in QIIME Artifact format (.qza). This file contains the taxonomy classifications for all reference sequences in the unfiltered dataset.
    * --m-ids-to-keep-file fish-refseqs.qza: Specifies a metadata file (in this case, a QIIME Artifact file containing sequence data) that lists the IDs of the sequences to retain. Only taxonomy entries corresponding to these sequence IDs in fish-refseqs.qza will be kept in the output.
    * --o-filtered-taxonomy fish-refseqs-taxonomy.qza: Specifies the output file for the filtered taxonomy (fish-refseqs-taxonomy.qza). This file will contain only taxonomy entries for the sequence IDs found in fish-refseqs.qza.

### 4. Training and Evaluating a Classifier
* Use RESCRIPt to train a Naive Bayes classifier with your filtered fish reference sequences and taxonomy.
* This command will fit a classifier (which usually takes a few minutes) and then test that classifier on all of the sequences found in the input, to give a best-case estimate of accuracy (i.e., when all query sequences have one or more known matches in the reference database). (Nicholas_Bokulich on Qiime2 Forum)
* `qiime rescript evaluate-fit-classifier --i-sequences fish-refseqs.qza --i-taxonomy fish-refseqs-taxonomy.qza --o-classifier fish-refseqs-classifier.qza --o-evaluation fish-refseqs-classifier-evaluation.qzv --o-observed-taxonomy fish-refseqs-predicted-taxonomy.qza`
    * qiime rescript evaluate-fit-classifier: uses the evaluate-fit-classifier function in the RESCRIPt plugin for QIIME 2, which trains a taxonomic classifier on the provided sequences and taxonomy, then tests the classifier's performance.
    * --i-sequences fish-refseqs.qza: Specifies the input sequence file (fish-refseqs.qza) in QIIME Artifact format (.qza). This file contains the filtered sequences to be used for training and testing the classifier.
    * --i-taxonomy fish-refseqs-taxonomy.qza: Specifies the input taxonomy file (fish-refseqs-taxonomy.qza) in QIIME Artifact format. This file contains the taxonomic labels for each sequence in fish-refseqs.qza, used as reference labels for training and evaluation.
    * --o-classifier fish-refseqs-classifier.qza: Specifies the output file for the trained classifier (fish-refseqs-classifier.qza). This file contains the classifier model, which can be applied to classify new sequence data.
    * --o-evaluation fish-refseqs-classifier-evaluation.qzv: Specifies the output file for the classifier evaluation results (fish-refseqs-classifier-evaluation.qzv). This file contains a visual summary of the classifier’s performance metrics across taxonomic levels, which can be viewed in QIIME 2 View.
    * --o-observed-taxonomy fish-refseqs-predicted-taxonomy.qza: Specifies the output file for the predicted taxonomy (fish-refseqs-predicted-taxonomy.qza). This file contains the taxonomic predictions made by the classifier on the input sequences, which allows for comparison between the predicted and actual taxonomy.

### 5. Test on eDNA Sequences (if available)
* If you have some eDNA sample data, you can apply your classifier:
* `qiime feature-classifier classify-sklearn --i-classifier fish-refseqs-classifier.qza --i-reads edna-sequences.qza --o-classification edna-taxonomy.qza`
    * qiime feature-classifier classify-sklearn: Uses the classify-sklearn function within the feature-classifier plugin in QIIME 2. It applies a trained Naive Bayes classifier (created earlier) to assign taxonomic labels to input sequences.
    * --i-classifier fish-refseqs-classifier.qza: Specifies the input classifier file (fish-refseqs-classifier.qza), which is a QIIME Artifact in .qza format. This file contains the trained taxonomic classifier for fish (Actinopterygii), which was previously trained.
    * --i-reads edna-sequences.qza: Specifies the input sequence file (edna-sequences.qza), which contains DNA sequences (such as those from environmental DNA) that need taxonomic classification. The classifier will predict the taxonomy for these sequences.
    * --o-classification edna-taxonomy.qza: Specifies the output file for the taxonomic classification results (edna-taxonomy.qza). This file will contain the predicted taxonomy for each sequence in edna-sequences.qza, formatted as a QIIME Artifact that can be visualized in QIIME 2 or further analyzed.

