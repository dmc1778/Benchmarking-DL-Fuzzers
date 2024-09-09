# Evaluating Deep Learning Fuzzers: A Comprehensive Benchmarking Study
Multiple API-level fuzzers test Deep Learning libraries in the literature. 
However, there is a gap here to check the effectiveness of these fuzzers on detecting real-world bugs/security vulnerabilities. 
In this project, we extensively compare DL fuzzers to understand their effectiveness on real-world bugs.

## :no_entry: Disclaimer :no_entry:
The fuzzers used in this project generate test cases designed to identify weaknesses in DL libraries. 
We strongly recommend running these tools in a sandbox or isolated environment, as they may crash or hang your operating system. 
Please avoid using any environment containing sensitive or critical information.

## Subject Library Versions
In this project, we use the latest releases of PyTorch and TensorFlow at the time we started this project.
We use versions 2.0.0, 2.0.1, and 2.1.0 for PyTorch and versions 2.11.0, 2.12.0, 2.13.0, and 2.14.0 for TensorFlow.

## Subject APIs
We use the following DL APIs for test case generation:

[PyTorch APIs](https://github.com/dmc1778/Benchmarking-DL-Fuzzers/blob/master/data/torch_apis.txt)

[TensorFlow APIs](https://github.com/dmc1778/Benchmarking-DL-Fuzzers/blob/master/data/tf_apis.txt)

:warning: Please note that we do not run the fuzzers on all DL APIs; we only evaluate them on the specific APIs mentioned.
These APIs are known to cause bugs in the subject releases of PyTorch and TensorFlow. 
If you wish to run the fuzzers on all APIs, you can still do so. However, 
the versions of the DL fuzzers provided in this replication package have been modified to focus exclusively on the mentioned APIs.

## DL Fuzzers
In this project, we target two groups of DL fuzzers.
### Traditional DL fuzzers
The traditional DL fuzzers used in this paper are as follows:

[FreeFuzz](https://github.com/ise-uiuc/FreeFuzz)

[DeepRel](https://github.com/ise-uiuc/DeepREL)

[NablaFuzz](https://github.com/ise-uiuc/NablaFuzz)

[DocTer](https://github.com/lin-tan/DocTer)

[ACETest](https://github.com/shijy16/ACETest)

### LLM-based DL fuzzers
We also used two recently introduced LLM-based DL fuzzers:

[TitanFuzz](https://github.com/ise-uiuc/TitanFuzz)

[AtlasFuzz](https://figshare.com/s/fc28098a692f24fb4b39)


## Getting started
### Create conda environments and install the required packages
To run the fuzzers, you need multiple conda environments. So, please install anaconda3 for Linux from the [this](https://docs.anaconda.com/anaconda/install/linux/) link.

After you successfully installed anaconda3 for Linux, run the following commands to create environments and install the required packages:

To create the environments, run the following commands:
```
bash create_envs_torch.sh
bash create_envs_tf.sh
```
:warning: Please note that all of the required packages for all of the subject fuzzers are installed once you create the conda environment.

Before running the fuzzers, you need to patch a bug within astuneparse library which is required by TitanFuzz and AtlasFuzz. Please read TitanFuzz's readme to fix the bug.

### Running DL Fuzzers and generating test cases
To run the subject DL fuzzers, you can use their source code from their replication packages. 
However, we recommend downloading the versions provided in this replication package. 
We have modified the argument parsing components to store the generated test cases for each library and its corresponding releases.
By using the versions in this package, you will save a lot of time.

You can find the versions under ```fuzzers``` directory.

#### Running NablaFuzz
Before running NablaFuzz, make sure that you have installed [mongodb](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/#std-label-install-mdb-community-ubuntu) community edition for Linux. NablaFuzz, DeepRel, and FreeFuzz depend on the MongoDB database as their test inputs are stored within the database. 

We use test inputs of NablaFuzz for FreeFuzz and DeepRel because NablaFuzz is the most recent fuzzers from the same authors and covers the highest number of APIs for both PyTorch and TensorFlow.

Once you installed MongoDB, run the following commands:

```
mongorestore NablaFuzz-PyTorch-Jax/dump
mongorestore NablaFuzz-TensorFlow/dump
```

The next step is to read PyTorch buggy APIs for test case generation, please follow:
```
cd NablaFuzz-PyTorch-Jax/src
```
Open ```torch_test.py``` and look for:

```
torch_valid_apis = read_txt('/media/nimashiri/SSD/fuzzers/NablaFuzz/torch_valid_apis.txt')
```
Please change it to a directory based on the location of the data file you want to set.

Also, do this for TensorFlow:

Open ```tf_adtest.py``` and look for:
```
tf_valid_apis = read_txt('/media/nimashiri/SSD/fuzzers/NablaFuzz/tf_valid_apis.txt')
```
Please change it to a directory based on the location of the data file you want to set.

Now, you have loaded the test inputs into the MongoDB database and are ready to run NablaFuzz, DeepRel, and FreeFuzz.

For example, to run NablaFuzz for PyTorch on the release 2.0.0, run the following command:

```
cd NablaFuzz-PyTorch-Jax/src
python torch_test.py --release 2.0.0 --iteration 5
```

to run NablaFuzz for TensorFlow on the release 2.11.0, run the following command:

```
cd NablaFuzz-TensorFlow/src
python tf_adtest.py --release 2.0.0 --iteration 5
```

PyTorch results can be found under ```output-ad``` and TensorFlow results are under ```expr_results``` directories.

#### Running DeepRel
To run DeepRel, please unzip the source to your desired directory, and run the following command to generate test cases for PyTorch:

```
cd DeepREL/pytorch/src
python DeepREL.py 2.0.0 torch
```
For TensorFlow:
```
cd DeepREL/tensorflow/src
python DeepREL.py 2.11.0 tf
```

#### Running FreeFuzz
To run FreeFuzz on PyTorch, please run the following commands:

```
cd /FreeFuzz/src
```
Then run:

```
python FreeFuzz.py --conf=FreeFuzz/src/config/expr.conf --release=2.0.0 --library=torch --iteration_round=5
```

For TensorFlow:

```
python FreeFuzz.py --conf=FreeFuzz/src/config/expr.conf --release=2.11.0 --library=tf --iteration_round=5
```


#### Running DocTer
To run DocTer, please unzip the source into your home directory. The path would be like ```/home/YOUR_USERNAME/code/doctor```.
Then activate your desired conda environment, e.g., ```tf.2.13.0```, and run the following command:
```
bash run_fuzzer.sh tensorflow ./all_constr/tf2 ./configs/vi.config 2.13.0 | tee /home/workdir/ci.log
```
For PyTorch, run the following command:
```
bash run_fuzzer.sh pytorch ./all_constr/tf2 ./configs/vi.config 2.0.0+cu118 | tee /home/workdir/ci.log
```

:warning: Please note that in our experiments, we used the torch versions with cuda enabled, i.e., ```2.0.0+cu118```, so depending on your version, this name can be changed.

After DocTer generates test cases, you have to run the following command to summarize the results for TensorFlow releases in the first iteration:

```
bash scripts/prepare_bug_list.sh /home/YOUR_USERNAME/workdir/tensorflow/1/2.11.0/conform_constr/
bash scripts/prepare_bug_list.sh /home/YOUR_USERNAME/workdir/tensorflow/1/2.12.0/conform_constr/
bash scripts/prepare_bug_list.sh /home/YOUR_USERNAME/workdir/tensorflow/1/2.13.0/conform_constr/
bash scripts/prepare_bug_list.sh /home/YOUR_USERNAME/workdir/tensorflow/1/2.14.0/conform_constr/
```
For PyTorch:
```
bash scripts/prepare_bug_list.sh /home/nima/workdir/pytorch/1/2.0.0+cu118/conform_constr/
bash scripts/prepare_bug_list.sh /home/nima/workdir/pytorch/1/2.0.1+cu118/conform_constr/
bash scripts/prepare_bug_list.sh /home/nima/workdir/pytorch/1/2.1.0+cu118/conform_constr/
```
#### Running ACETest
Please unzip the source to your desired directory and cd to the root.
To run ACETest on PyTorch, run the following command:

```
python main.py --test_round=1000 --mode=all --release=2.0.0 --framework=torch --work_path=output --filter=all
python main.py --test_round=1000 --mode=all --release=2.0.1 --framework=torch --work_path=output --filter=all
python main.py --test_round=1000 --mode=all --release=2.1.0 --framework=torch --work_path=output --filter=all
```

For TensorFlow:

```
python main.py --test_round=1000 --mode=all --release=2.11.0 --framework=tf --work_path=output --filter=all
python main.py --test_round=1000 --mode=all --release=2.12.0 --framework=tf --work_path=output --filter=all
python main.py --test_round=1000 --mode=all --release=2.13.0 --framework=tf --work_path=output --filter=all
python main.py --test_round=1000 --mode=all --release=2.14.0 --framework=tf --work_path=output --filter=all
```

#### Running TitanFuzz
First, change your directory to TitanFuzz root, then run it using the following command for PyTorch library:

```
bash scripts/local_run.sh torch data/torch_applicable_apis.txt torch_2.0.1 and 2.0.1 5
```
For TensorFlow:

```
bash scripts/local_run.sh tf data/tf_applicable_apis.txt tf_2.11.0 and 2.11.1 5
```

#### Running AtlasFuzz


