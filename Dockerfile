FROM python:3.10.12
COPY ./app /app
WORKDIR /app

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y cmake
RUN pip install --upgrade pip setuptools wheel

RUN pip uninstall llvmlite
RUN apt-get install -y llvm
ENV LLVM_CONFIG=/usr/bin/llvm-config
RUN pip install llvmlite

RUN pip install pytorch_lightning
RUN pip install torchcrepe==0.0.17
RUN pip install praat-parselmouth==0.4.3
RUN pip install scikit-image==0.19.3
RUN pip install ipython==7.34.0
RUN pip install ipykernel==5.5.6
RUN pip install pyloudnorm==0.1.0
RUN pip install webrtcvad==2.0.10
RUN pip install h5py==3.7.0
RUN pip install einops==0.5.0
RUN pip install pycwt==0.3.0a22
RUN pip install torchmetrics==0.5
RUN pip install pytorch_lightning
RUN pip install pyworld
RUN pip uninstall numba --yes
RUN pip install numba
RUN pip install pydub

RUN pip install -r requirements.txt

FROM test:latest

RUN rm -rf sample_data
RUN python -m pip install --upgrade pip wheel --quiet
RUN pip uninstall gdown -y --quiet
#!pip install git+https://github.com/justinjohn0306/gdown.git --quiet
RUN pip install pydub fuzzywuzzy python-Levenshtein pyworld==0.3.1 --quiet

#install aria2
RUN sudo apt-get install aria2  &> /dev/null
RUN apt install wget curl ca-certificates &> /dev/null
RUN wget -N git.io/aria2.sh &> /dev/null && chmod +x aria2.sh &> /dev/null
RUN echo 1|./aria2.sh &> /dev/null
RUN echo 12|./aria2.sh &> /dev/null
RUN echo 6|./aria2.sh &> /dev/null
RUN pip install --pre torchtext==0.6.0 --no-deps --quiet

RUN git clone --branch harvest-preprocess https://github.com/UtaUtaUtau/diff-svc.git && cd diff-svc && pip install -r requirements_short.txt --quiet
RUN pip install tensorboard<2.9,>=2.8 --quiet
#!pip install —upgrade numpy==1.23.0 scipy==1.9.3 —quiet
RUN reload_ext tensorboard

RUN mkdir -p checkpoints

RUN echo "https://github.com/haru0l/Diff-SVC-notebooks/releases/download/models_24khz/hifigan_24k.zip" > hifigan_24k
RUN echo "https://github.com/haru0l/Diff-SVC-notebooks/releases/download/start/hifigan_44k.zip" > hifigan_44k
RUN echo "https://github.com/haru0l/Diff-SVC-notebooks/releases/download/start/checkpoints.zip" > checkpoints

RUN aria2c —file-allocation=none -c -x 10 -s 10 {checkpoints} -q
RUN unzip checkpoints.zip
RUN rm checkpoints.zip

RUN aria2c —file-allocation=none -c -x 10 -s 10 {hifigan_24k} -q
RUN unzip hifigan_24k.zip
RUN rm hifigan_24k.zip
RUN config_path = "training/config.yaml"
RUN rm {config_path}
RUN wget "https://github.com/haru0l/Diff-SVC-notebooks/releases/download/models_24khz/config.yaml" -O {config_path} -q
RUN slay = "24000"
RUN clear_output()

EXPOSE 80
COPY ./app/DiffSVC.ipynb /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]