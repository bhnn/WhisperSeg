import argparse

import ctranslate2
from transformers import WhisperConfig, WhisperTokenizer


def convert_hf_to_ct2(
        model: str, output_dir: str, quantization: str = None, load_as_float16: bool = False,
        low_cpu_mem_usage: bool = False, trust_remote_code: bool = False, force: bool = False,
    ) -> None:
    converter = ctranslate2.converters.TransformersConverter(
        model_name_or_path = model,
        load_as_float16 = load_as_float16,
        low_cpu_mem_usage = low_cpu_mem_usage,
        trust_remote_code = trust_remote_code,
    )
    converter.convert(
        output_dir = output_dir,
        quantization = quantization,
        force = force,
    )
    ## save original tokenizer
    tokenizer = WhisperTokenizer.from_pretrained(model)
    tokenizer.save_pretrained(output_dir + "/hf_model")
    ## save original model configuration
    config = WhisperConfig.from_pretrained(model)
    config.save_pretrained(output_dir + "/hf_model")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--quantization", default = None, help="can be int8, float16 and int8_float16, if it is not set, then do not apply quantization")
    parser.add_argument("--load_as_float16", action="store_true")
    parser.add_argument("--low_cpu_mem_usage", action="store_true")
    parser.add_argument("--trust_remote_code", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    convert_hf_to_ct2(**vars(args))