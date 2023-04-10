import subprocess

TF_RELEASE_CUDA_MAP = {
    "2.4.0": "11.0",
    "2.3.0": "10.1",
}

TF_RELEASE_CUDNN_MAP = {
    "2.4.0": "8.0",
    "2.3.0": "7.6",
}

# Loop over TensorFlow releases
for tf_version, _ in TF_RELEASE_CUDA_MAP.items():

    env_name_tf = f"fuzzer_tf_{tf_version}"
    subprocess.call(
        [
            "/media/nimashiri/DATA/vsprojects/benchmarkingDLFuzzers/benchmarking/setup_and_run_tf.sh",
            env_name_tf,
            tf_version,
            "tf",
        ],
        shell=False,
    )

    print("")
