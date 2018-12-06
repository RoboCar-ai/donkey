FROM tensorflow/tensorflow:latest-py3
COPY . /robocar
WORKDIR /robocar
ADD tensorflow-1.12.0-cp35-cp35m-linux_x86_64.whl .
RUN pip install --ignore-installed --upgrade tensorflow-1.12.0-cp35-cp35m-linux_x86_64.whl
# RUN apt install -y python3 python3-dev python3-pip
# RUN pip3 install pip six numpy wheel mock
# RUN pip3 install keras_applications==1.0.5 --no-deps
# RUN pip3 install keras_preprocessing==1.0.3 --no-depsi
# RUN apt-get install -y pkg-config zip g++ zlib1g-dev unzip python curl git
# RUN apt-get install openjdk-8-jdk && echo "deb [arch=amd64] http://storage.googleapis.com/bazel-apt stable jdk1.8" | tee /etc/apt/sources.list.d/bazel.list && curl https://bazel.build/bazel-release.pub.gpg | apt-key add -
# RUN apt-get update && apt-get -y install bazel
# RUN git clone https://github.com/tensorflow/tensorflow.git && cd tensorflow && git checkout r1.12

#RUN conda install tensorflow && pip install scikit-learn 
RUN pip install -e . && donkey createcar --path d2
WORKDIR /robocar/d2 
#RUN pip3  && pip3 install scikit-learn

