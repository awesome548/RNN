from pyexpat import model
from unicodedata import bidirectional
from xml.etree.ElementInclude import include
from sentry_sdk import configure_scope
import torch
import click
from pytorch_lightning.loggers import WandbLogger
from torch.utils.data import  random_split
import pytorch_lightning as pl
from lstm import LstmEncoder,CNNLstmEncoder
from transformer import ViTransformer
from cnn import ResNet, Bottleneck
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from datamodule import DataModule
from preprocess import Preprocess
import glob
from dataformat import Dataformat


@click.command()
@click.option('--target', '-t', help='The path of positive sequence training set', type=click.Path(exists=True))
# Inpath is the taget directory of all dataset
@click.option('--inpath', '-i', help='The path of positive sequence training set', type=click.Path(exists=True))
@click.option('--arch', '-a', help='The path of positive sequence training set')

@click.option('--batch', '-b', default=100, help='Batch size, default 1000')
@click.option('--epoch', '-e', default=40, help='Number of epoches, default 20')
@click.option('--learningrate', '-l', default=1e-2, help='Learning rate, default 1e-3')
@click.option('--cutlen', '-len', default=3000, help='Cutting length')
@click.option('--cutoff', '-off', default=1500, help='Cutting length')
@click.option('--classes', '-class', default=3, help='Num of class')


def main(target,inpath,arch, batch, epoch, learningrate,cutlen,cutoff,classes):

    """
    Change Preference
    """
    project_name = "ResNet"

    ### MODEL SELECT ###
    useResNet = False
    useTransformer = False
    useLstm = False
    if "ResNet" in str(arch):
        transform = False 
        useResNet = True
    elif "LSTM" in str(arch):
        transform = True
        useLstm = True 
    else:
        assert str(arch) == "Transformer"
        transform = True
        useTransformer = True 
    useModel = arch 
    #####################

    """
    Dataset Preference
    """
    num_classes = classes 
    dataset_size = 7000
    inputDim = 1
    data_transform = {
        'isFormat' : transform,
        'dim' : inputDim,
        'length' : cutlen,
    }
    cut_size = {
        'cutoff' : cutoff,
        'cutlen' : cutlen,
        'maxlen' : 10000,  
        'stride' : 5000,
    }

    idset = glob.glob(target+'/*.txt')
    dataset = glob.glob(inpath+'/*')

    data = Dataformat(idset,dataset,dataset_size,cut_size,num_classes=num_classes,transform=data_transform)
    data_module = data.process(batch)
    dataset_size = data.size()
    ### Torch setting ###
    if torch.cuda.is_available:device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    ### PREPARATION ###
    """
    Logger setting
    """
    wandb_logger = WandbLogger(
        project=project_name,
        config={
            "num_clasess": classes,
            "dataset_size" : dataset_size,
            "model" : useModel, 
            "cutlen" : cutlen,
        },
        name=useModel+"_"+str(num_classes)+"_"+str(cutlen)
    )
    """
    Parameter setting
    """
    cnn_params = {
        'padd' : 5,
        'ker' : 19,
        'stride' : 3,
        'convDim' : 20,
    }
    lstm_params = {
        'inputDim' : inputDim,
        'hiddenDim' : 128,
        'outputDim' : num_classes,
        'bidirect' : True
    }
    transformer_params = {
        'classes' : num_classes,
        'head_num' : 4,
        'block_num' : 4,
        'length' : cutlen 
    }


    """
    MODEL architecture
    """
    if useLstm:
        model = CNNLstmEncoder(**lstm_params,lr=learningrate,classes=num_classes)
    elif useResNet:
        model = ResNet(Bottleneck,[2,2,2,2],classes=num_classes,cutlen=cutlen,lr=learningrate)
    elif useTransformer:
        model = ViTransformer(**transformer_params,lr=learningrate,batch=batch)

    # refine callbacks
    early_stopping = EarlyStopping(
        monitor="valid_loss",
        mode="min",
        patience=10,
    )

    trainer = pl.Trainer(
        max_epochs=epoch,
        min_epochs=30,
        accelerator="gpu",
        devices=torch.cuda.device_count(),
        logger=wandb_logger,
        callbacks=[early_stopping],
        # callbacks=[model_checkpoint],
    )
    trainer.fit(
        model,
        datamodule=data_module,
    )
    trainer.test(
        model,
        datamodule=data_module,
    )


if __name__ == '__main__':
    main()
