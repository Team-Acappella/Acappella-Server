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
RUN pip install praat-parselmouth==0.4.1
RUN pip install scikit-image==0.19.3
RUN pip install ipython==7.34.0
RUN pip install ipykernel==5.5.6
RUN pip install pyloudnorm==0.1.0
RUN pip install webrtcvad==2.0.10
RUN pip install h5py==3.7.0
RUN pip install einops==0.5.0
RUN pip install pycwt==0.3.0a22
RUN pip install torchmetrics==0.5
RUN pip install pytorch_lightning==1.3.3
RUN pip install pyworld
RUN pip uninstall numba --yes
RUN pip install numba
RUN pip install pydub

RUN pip install -r requirements.txt
EXPOSE 80
COPY ./app/DiffSVC.ipynb /app
COPY ./app/test.ipynb /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]