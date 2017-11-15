import boto3
import os
import sys
from tqdm import tqdm
from botocore import UNSIGNED
from botocore.client import Config
from botocore.handlers import disable_signing

from dataset.s3.index import Indexer
from dataset.s3.local_writer import Writer
from util.log_helper import LogHelper


if __name__ == "__main__":
    block = int(sys.argv[1])-1

    LogHelper.setup()
    logger = LogHelper.get_logger(__name__)
    logger.info("Downloading Block of Pages from Dataset")
    logger.info("Block Number: {0}".format(block))

    logger.debug("Checking if fever data dir exists")
    intro_path = os.path.join("data", "fever")
    if not os.path.exists(intro_path):
        logger.debug("Creating data dir")
        os.makedirs(intro_path)


    #Use boto3 to download all pages from intros section from s3
    client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    resource = boto3.resource("s3")
    resource.meta.client.meta.events.register('choose-signer.s3.*', disable_signing)

    block_keys = []
    with open(os.path.join("data","fever","pages.p"),"wb+") as f:
        indexer = Indexer(f)
        indexer.load()
        block_keys.extend(indexer.get_block(block))

    with Writer(block,"page",os.path.join("data","fever")) as writer:
        for key in tqdm(block_keys):
            full_key = "wiki-dump/intro/"+key
            obj = client.get_object(Bucket=os.getenv("S3_BUCKET"), Key=full_key)

            writer.save(key, obj["Body"].read().decode("utf-8"))
