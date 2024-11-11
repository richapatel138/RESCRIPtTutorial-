import subprocess

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(e.stderr)

# Step 1: Download Fish Sequence Data from NCBI with RESCRIPt
run_command("qiime rescript get-ncbi-data --p-query 'Actinopterygii[Organism] AND \"complete genome\"[Title]' --o-sequences fish-refseqs-unfiltered.qza --o-taxonomy fish-refseqs-taxonomy-unfiltered.qza --p-n-jobs 3")

# Step 2: Filter Sequences by Length
run_command("qiime rescript filter-seqs-length-by-taxon --i-sequences fish-refseqs-unfiltered.qza --i-taxonomy fish-refseqs-taxonomy-unfiltered.qza --p-labels Actinopterygii --p-min-lens 10000 --p-max-lens 20000 --o-filtered-seqs fish-refseqs.qza --o-discarded-seqs fish-refseqs-tooshortorlong.qza")

# Step 3: Filter the Taxonomy File
run_command("qiime rescript filter-taxa --i-taxonomy fish-refseqs-taxonomy-unfiltered.qza --m-ids-to-keep-file fish-refseqs.qza --o-filtered-taxonomy fish-refseqs-taxonomy.qza")

# Step 4: Train and Evaluate a Classifier
run_command("qiime rescript evaluate-fit-classifier --i-sequences fish-refseqs.qza --i-taxonomy fish-refseqs-taxonomy.qza --o-classifier fish-refseqs-classifier.qza --o-evaluation fish-refseqs-classifier-evaluation.qzv --o-observed-taxonomy fish-refseqs-predicted-taxonomy.qza")
